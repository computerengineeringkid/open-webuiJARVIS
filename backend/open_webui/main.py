"""Minimal FastAPI application focused on chat functionality."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from open_webui.config import API_PREFIX, ALLOWED_ORIGINS
from open_webui.routers import chats, ollama
from open_webui.storage.chat_store import get_chat_store, shutdown_chat_store


app = FastAPI(title="Open WebUI Chat API")


app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
async def startup_event() -> None:
    # Ensure the chat store is initialised during startup.
    get_chat_store()


@app.on_event("shutdown")
async def shutdown_event() -> None:
    shutdown_chat_store()


app.include_router(chats.router, prefix=f"{API_PREFIX}/chats", tags=["chats"])
app.include_router(ollama.router, prefix=f"{API_PREFIX}/models", tags=["models"])


@app.get("/health", tags=["health"])
async def health_check() -> dict[str, str]:
    return {"status": "ok"}
