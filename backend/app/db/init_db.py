from pathlib import Path
import random
from datetime import date, timedelta
import pandas as pd
from sqlalchemy import text
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from app.db.session import engine

DATA_DIR = Path(__file__).resolve().parents[2] / "data"
CSV_DIR = DATA_DIR / "csv"
PDF_DIR = DATA_DIR / "pdfs"
DB_PATH = DATA_DIR / "insights.db"

MOVIES = [
    ("Stellar Run", "Sci-Fi", "2025-01-10"),
    ("Dark Orbit", "Sci-Fi", "2025-03-22"),
    ("Last Kingdom", "Drama", "2025-02-14"),
    ("Laugh Track", "Comedy", "2025-04-05"),
    ("City Lights", "Romance", "2025-05-15"),
    ("Mystery Lake", "Thriller", "2025-06-11"),
    ("Family Weekend", "Comedy", "2025-07-18"),
    ("Neon Beats", "Music", "2025-08-02"),
]
CITIES = ["Mumbai", "Delhi", "Bengaluru", "Hyderabad", "Chennai", "Pune", "Kolkata"]
SEGMENTS = ["Gen Z", "Millennials", "Families", "Premium", "Casual"]


def ensure_dirs():
    CSV_DIR.mkdir(parents=True, exist_ok=True)
    PDF_DIR.mkdir(parents=True, exist_ok=True)


def make_csvs(seed: int = 42):
    random.seed(seed)
    movies = pd.DataFrame([
        {"movie_id": i + 1, "title": t, "genre": g, "release_date": r, "production_budget_m": random.randint(18, 95)}
        for i, (t, g, r) in enumerate(MOVIES)
    ])
    movies.to_csv(CSV_DIR / "movies.csv", index=False)

    viewers = []
    for i in range(1, 901):
        viewers.append({
            "viewer_id": i,
            "city": random.choice(CITIES),
            "segment": random.choice(SEGMENTS),
            "signup_date": str(date(2024, 1, 1) + timedelta(days=random.randint(0, 560)))
        })
    pd.DataFrame(viewers).to_csv(CSV_DIR / "viewers.csv", index=False)

    activities, reviews, spend, regional = [], [], [], []
    start = date(2025, 1, 1)
    for day in range(300):
        d = start + timedelta(days=day)
        for movie_id, title, genre, _ in [(i+1, *m) for i, m in enumerate(MOVIES)]:
            base = {"Stellar Run": 950, "Dark Orbit": 700, "Last Kingdom": 660, "Laugh Track": 260, "Family Weekend": 220}.get(title, 420)
            trend = 1 + (0.55 if title == "Stellar Run" and day > 220 else 0) + (0.25 if genre == "Sci-Fi" and day > 170 else 0)
            if genre == "Comedy" and day > 120:
                trend *= 0.72
            views = max(30, int(random.gauss(base * trend, 75)))
            watch_minutes = views * random.randint(38, 88)
            completion_rate = round(min(0.95, max(0.34, random.gauss(0.69 if genre != "Comedy" else 0.51, 0.08))), 2)
            activities.append({"activity_date": str(d), "movie_id": movie_id, "views": views, "watch_minutes": watch_minutes, "completion_rate": completion_rate})
            if day % 7 == 0:
                sentiment = random.gauss(4.25 if title == "Stellar Run" else 3.75 if genre != "Comedy" else 2.95, 0.45)
                reviews.append({"review_date": str(d), "movie_id": movie_id, "avg_rating": round(min(5, max(1, sentiment)), 2), "review_count": random.randint(25, 240)})
            if day % 30 == 0:
                spend.append({"month": str(d.replace(day=1)), "movie_id": movie_id, "channel": random.choice(["Social", "Search", "Influencer", "TV"]), "spend_k": random.randint(20, 450)})
            if day % 14 == 0:
                for city in CITIES:
                    regional.append({"period_start": str(d), "movie_id": movie_id, "city": city, "engagement_score": round(random.gauss(72 if city == "Bengaluru" and genre == "Sci-Fi" else 58, 11), 2)})
    pd.DataFrame(activities).to_csv(CSV_DIR / "watch_activity.csv", index=False)
    pd.DataFrame(reviews).to_csv(CSV_DIR / "reviews.csv", index=False)
    pd.DataFrame(spend).to_csv(CSV_DIR / "marketing_spend.csv", index=False)
    pd.DataFrame(regional).to_csv(CSV_DIR / "regional_performance.csv", index=False)


def load_sqlite():
    for path in CSV_DIR.glob("*.csv"):
        pd.read_csv(path).to_sql(path.stem, engine, if_exists="replace", index=False)
    with engine.begin() as conn:
        conn.execute(text("CREATE INDEX IF NOT EXISTS idx_watch_movie_date ON watch_activity(movie_id, activity_date)"))
        conn.execute(text("CREATE INDEX IF NOT EXISTS idx_regional_movie_city ON regional_performance(movie_id, city)"))


def write_pdf(filename: str, title: str, lines: list[str]):
    c = canvas.Canvas(str(PDF_DIR / filename), pagesize=letter)
    width, height = letter
    y = height - 60
    c.setFont("Helvetica-Bold", 16)
    c.drawString(50, y, title)
    y -= 35
    c.setFont("Helvetica", 10)
    for line in lines:
        for chunk in [line[i:i+95] for i in range(0, len(line), 95)]:
            c.drawString(50, y, chunk)
            y -= 16
            if y < 60:
                c.showPage(); y = height - 60; c.setFont("Helvetica", 10)
        y -= 6
    c.save()


def make_pdfs():
    docs = {
        "quarterly_executive_report.pdf": ("Quarterly Executive Report", [
            "Stellar Run became the breakout title in Q3 2025 due to strong sci-fi demand, repeat viewing, and social conversation around the finale.",
            "Comedy titles underperformed because campaign creative tested poorly with Gen Z and completion rates were below company benchmarks.",
            "Leadership should increase investment in premium sci-fi, refresh comedy positioning, and localize campaigns in Bengaluru and Mumbai."
        ]),
        "campaign_performance_summary.pdf": ("Campaign Performance Summary", [
            "Influencer campaigns produced the strongest lift for Stellar Run, especially after short-form clips highlighted world-building and character arcs.",
            "Search spend had efficient acquisition for Dark Orbit but lower retention than Stellar Run.",
            "TV spend for comedy produced broad reach but weak conversion and should be reduced until creative is improved."
        ]),
        "content_roadmap.pdf": ("Content Roadmap", [
            "The roadmap prioritizes sci-fi sequels, thriller limited series, and fewer mid-budget comedies next quarter.",
            "A spin-off for Stellar Run is recommended if sentiment remains above 4.1 and completion rate remains above 70 percent.",
            "Comedy slate needs sharper audience targeting and earlier concept testing."
        ]),
        "policy_guidelines.pdf": ("Policy Guidelines", [
            "Internal analytics assistants must not expose raw viewer personal data, emails, phone numbers, or unrestricted database access.",
            "Business answers should cite approved structured, spreadsheet, and document sources where possible.",
            "Users should access only tools allowed by their role."
        ]),
        "audience_behavior_report.pdf": ("Audience Behavior Report", [
            "Bengaluru and Mumbai showed the highest engagement for sci-fi titles, with premium and Gen Z segments driving repeat viewing.",
            "Families watched comedy but churned quickly when completion rates were low.",
            "Stellar Run trended because social discovery, high completion, and positive reviews reinforced each other."
        ]),
    }
    for filename, (title, lines) in docs.items():
        write_pdf(filename, title, lines)


def init():
    ensure_dirs(); make_csvs(); load_sqlite(); make_pdfs()
    print(f"Initialized demo data in {DATA_DIR}")

if __name__ == "__main__":
    init()
