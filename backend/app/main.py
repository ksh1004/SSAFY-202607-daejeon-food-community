from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import get_settings
from app.database import Base, engine
from app.routers import chat, posts, restaurants

settings = get_settings()

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="LocalHub Backend API",
    version="1.0.0",
    description="대전·충청권 음식점 데이터와 익명 게시판을 제공하는 FastAPI 서버",
)

origins = {
    "http://localhost:5173",
    settings.frontend_origin.rstrip("/"),
}

app.add_middleware(
    CORSMiddleware,
    allow_origins=list(origins),
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(restaurants.router)
app.include_router(posts.router)
app.include_router(chat.router)


@app.get("/")
def root() -> dict[str, str]:
    return {
        "service": "LocalHub Backend API",
        "status": "running",
        "docs": "/docs",
    }


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}
