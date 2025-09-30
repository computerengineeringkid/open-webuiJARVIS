"""Model interaction endpoints that proxy requests to an Ollama instance."""

from __future__ import annotations

from typing import Any, AsyncIterator

import httpx
from fastapi import APIRouter, HTTPException, Request, status
from fastapi.responses import StreamingResponse

from open_webui.config import OLLAMA_BASE_URL


router = APIRouter()


@router.get("/", summary="List available models")
async def list_models() -> dict[str, Any]:
    async with httpx.AsyncClient(base_url=OLLAMA_BASE_URL, timeout=None) as client:
        response = await client.get("/api/tags")
    if response.status_code != status.HTTP_200_OK:
        raise HTTPException(response.status_code, response.text)
    return response.json()


@router.post("/generate", summary="Generate a response from a model")
async def generate(request: Request) -> StreamingResponse:
    payload = await request.body()

    async def _proxy() -> AsyncIterator[bytes]:
        async with httpx.AsyncClient(base_url=OLLAMA_BASE_URL, timeout=None) as client:
            async with client.stream(
                "POST",
                "/api/generate",
                content=payload,
                headers={"content-type": "application/json"},
            ) as response:
                if response.status_code != status.HTTP_200_OK:
                    body = await response.aread()
                    raise HTTPException(response.status_code, body.decode() or response.reason_phrase)
                async for chunk in response.aiter_bytes():
                    yield chunk

    return StreamingResponse(_proxy(), media_type="application/json")
