from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.routes import router
from app.core.config import get_settings
from app.db.init_db import init
from dotenv import load_dotenv
load_dotenv()

settings = get_settings()
app = FastAPI(title="Secure AI Insights Assistant", version="1.0.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(router, prefix="/api")

@app.on_event("startup")
def startup():
    init()
