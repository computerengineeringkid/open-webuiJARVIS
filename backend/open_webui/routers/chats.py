"""Chat endpoints."""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status

from open_webui.models.chat import Chat, ChatCreate, ChatUpdate, Message, MessageCreate
from open_webui.storage.chat_store import ChatStore, get_chat_store


router = APIRouter()


def get_store() -> ChatStore:
    return get_chat_store()


@router.get("/", response_model=list[Chat])
async def list_chats(store: ChatStore = Depends(get_store)) -> list[Chat]:
    return list(store.list_chats())


@router.post("/", response_model=Chat, status_code=status.HTTP_201_CREATED)
async def create_chat(form: ChatCreate, store: ChatStore = Depends(get_store)) -> Chat:
    return store.create_chat(form)


@router.get("/{chat_id}", response_model=Chat)
async def get_chat(chat_id: str, store: ChatStore = Depends(get_store)) -> Chat:
    chat = store.get_chat(chat_id)
    if not chat:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Chat not found")
    return chat


@router.put("/{chat_id}", response_model=Chat)
async def update_chat(
    chat_id: str, form: ChatUpdate, store: ChatStore = Depends(get_store)
) -> Chat:
    chat = store.update_chat(chat_id, form)
    if not chat:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Chat not found")
    return chat


@router.delete("/{chat_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_chat(chat_id: str, store: ChatStore = Depends(get_store)) -> None:
    deleted = store.delete_chat(chat_id)
    if not deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Chat not found")


@router.post("/{chat_id}/messages", response_model=Message, status_code=status.HTTP_201_CREATED)
async def add_message(
    chat_id: str, form: MessageCreate, store: ChatStore = Depends(get_store)
) -> Message:
    message = store.add_message(chat_id, form)
    if not message:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Chat not found")
    return message
