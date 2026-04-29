import re
from fastapi import HTTPException, Request

PII_PATTERNS = [
    re.compile(r"[\w\.-]+@[\w\.-]+\.\w+"),
    re.compile(r"\b(?:\+?\d{1,3}[-.\s]?)?(?:\d{10}|\d{3}[-.\s]\d{3}[-.\s]\d{4})\b"),
]

BLOCKED_SQL = re.compile(r"\b(insert|update|delete|drop|alter|truncate|attach|pragma|replace)\b", re.I)

ROLE_PERMISSIONS = {
    "leadership": {"analytics", "documents", "recommendations"},
    "analyst": {"analytics", "documents"},
    "viewer": {"analytics"},
}

def redact_sensitive(text: str) -> str:
    redacted = text
    for pat in PII_PATTERNS:
        redacted = pat.sub("[REDACTED]", redacted)
    return redacted

def require_scope(request: Request, scope: str) -> None:
    role = request.headers.get("x-user-role", "leadership").lower()
    if scope not in ROLE_PERMISSIONS.get(role, set()):
        raise HTTPException(status_code=403, detail=f"Role '{role}' cannot access scope '{scope}'")

def validate_readonly_sql(sql: str) -> None:
    normalized = sql.strip().lower()
    if not (normalized.startswith("select") or normalized.startswith("with")):
        raise HTTPException(status_code=400, detail="Only SELECT/CTE queries are allowed")
    if BLOCKED_SQL.search(sql):
        raise HTTPException(status_code=400, detail="Unsafe SQL keyword blocked")
    if ";" in sql[:-1]:
        raise HTTPException(status_code=400, detail="Multiple SQL statements are not allowed")
