import pandas as pd
from sqlalchemy import text
from app.core.config import get_settings
from app.core.security import validate_readonly_sql
from app.db.session import engine

settings = get_settings()

SCHEMA_HINT = """
Tables:
movies(movie_id,title,genre,release_date,production_budget_m)
viewers(viewer_id,city,segment,signup_date)
watch_activity(activity_date,movie_id,views,watch_minutes,completion_rate)
reviews(review_date,movie_id,avg_rating,review_count)
marketing_spend(month,movie_id,channel,spend_k)
regional_performance(period_start,movie_id,city,engagement_score)
"""

SAFE_QUERY_LIBRARY = {
    "top_titles_2025": """
        SELECT m.title, m.genre, SUM(w.views) AS total_views,
               SUM(w.watch_minutes) AS total_watch_minutes,
               ROUND(AVG(w.completion_rate), 3) AS avg_completion,
               ROUND(AVG(r.avg_rating), 2) AS avg_rating
        FROM watch_activity w
        JOIN movies m ON m.movie_id = w.movie_id
        LEFT JOIN reviews r ON r.movie_id = m.movie_id
        WHERE w.activity_date BETWEEN '2025-01-01' AND '2025-12-31'
        GROUP BY m.movie_id, m.title, m.genre
        ORDER BY total_views DESC
        LIMIT 10
    """,
    "city_engagement_last_month": """
        SELECT city, ROUND(AVG(engagement_score), 2) AS avg_engagement
        FROM regional_performance
        WHERE period_start >= '2025-09-01'
        GROUP BY city
        ORDER BY avg_engagement DESC
    """,
    "genre_growth": """
        WITH monthly AS (
            SELECT m.genre, substr(w.activity_date,1,7) AS month, SUM(w.views) AS views
            FROM watch_activity w JOIN movies m ON m.movie_id=w.movie_id
            GROUP BY m.genre, substr(w.activity_date,1,7)
        )
        SELECT genre,
               SUM(CASE WHEN month <= '2025-03' THEN views ELSE 0 END) AS early_views,
               SUM(CASE WHEN month >= '2025-08' THEN views ELSE 0 END) AS recent_views,
               ROUND((SUM(CASE WHEN month >= '2025-08' THEN views ELSE 0 END) * 1.0 / NULLIF(SUM(CASE WHEN month <= '2025-03' THEN views ELSE 0 END),0))-1, 3) AS growth_rate
        FROM monthly GROUP BY genre ORDER BY growth_rate DESC
    """,
    "title_compare": """
        SELECT m.title, m.genre, SUM(w.views) AS total_views,
               SUM(w.watch_minutes) AS watch_minutes,
               ROUND(AVG(w.completion_rate),3) AS completion,
               ROUND(AVG(r.avg_rating),2) AS rating,
               SUM(ms.spend_k) AS total_marketing_spend_k
        FROM movies m
        LEFT JOIN watch_activity w ON w.movie_id=m.movie_id
        LEFT JOIN reviews r ON r.movie_id=m.movie_id
        LEFT JOIN marketing_spend ms ON ms.movie_id=m.movie_id
        WHERE m.title IN ('Dark Orbit','Last Kingdom')
        GROUP BY m.movie_id, m.title, m.genre
    """,
    "comedy_performance": """
        SELECT m.title, SUM(w.views) AS views, ROUND(AVG(w.completion_rate),3) AS completion,
               ROUND(AVG(r.avg_rating),2) AS rating, SUM(ms.spend_k) AS spend_k
        FROM movies m
        LEFT JOIN watch_activity w ON w.movie_id=m.movie_id
        LEFT JOIN reviews r ON r.movie_id=m.movie_id
        LEFT JOIN marketing_spend ms ON ms.movie_id=m.movie_id
        WHERE m.genre='Comedy'
        GROUP BY m.title
        ORDER BY views DESC
    """,
}

def run_sql(sql: str) -> list[dict]:
    validate_readonly_sql(sql)
    limited_sql = sql.strip().rstrip(";") + f" LIMIT {settings.max_query_rows}" if " limit " not in sql.lower() else sql
    return pd.read_sql_query(text(limited_sql), engine).to_dict(orient="records")

def run_named_query(name: str) -> list[dict]:
    if name not in SAFE_QUERY_LIBRARY:
        raise ValueError(f"Unknown query '{name}'")
    return run_sql(SAFE_QUERY_LIBRARY[name])
