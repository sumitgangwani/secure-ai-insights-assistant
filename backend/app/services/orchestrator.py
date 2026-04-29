from app.tools.sql_tool import run_named_query
from app.services.document_service import retriever
from app.services.ai_service import generate_answer

QUESTION_ROUTES = [
    (["best", "performed", "2025", "top"], ["top_titles_2025", "genre_growth"]),
    (["stellar run", "trending"], ["top_titles_2025"]),
    (["dark orbit", "last kingdom", "compare"], ["title_compare"]),
    (["city", "engagement", "last month"], ["city_engagement_last_month"]),
    (["weak", "comedy"], ["comedy_performance"]),
    (["recommend", "leadership"], ["top_titles_2025", "genre_growth", "city_engagement_last_month", "comedy_performance"]),
]

def select_queries(question: str) -> list[str]:
    q = question.lower()
    selected: list[str] = []
    for terms, queries in QUESTION_ROUTES:
        if any(t in q for t in terms):
            selected.extend(queries)
    if not selected:
        selected = ["top_titles_2025", "genre_growth"]
    return list(dict.fromkeys(selected))

def answer_question(question: str) -> dict:
    selected = select_queries(question)
    sql_results = {name: run_named_query(name) for name in selected}
    doc_results = retriever.search(question, k=6)
    tool_results = {"sql": sql_results, "documents": doc_results}
    answer = generate_answer(question, tool_results)
    return {
        "answer": answer,
        "sources": {
            "sql_queries": selected,
            "documents": [{"source": d["source"], "score": d["score"]} for d in doc_results],
        },
        "tool_trace": [
            {"tool": "sql_named_query", "input": name, "rows": len(sql_results[name])} for name in selected
        ] + [{"tool": "document_retrieval", "input": question, "rows": len(doc_results)}],
        "raw": tool_results,
    }
