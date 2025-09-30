"""Thread-safe JSON backed chat storage."""

from __future__ import annotations

import json
import threading
from datetime import datetime
from pathlib import Path
from typing import Dict, Iterable, Optional

from open_webui.config import CHAT_STORAGE_PATH
from open_webui.models.chat import Chat, ChatCreate, ChatUpdate, Message, MessageCreate


class ChatStore:
    """Simple JSON backed store used by the chat router."""

    def __init__(self, storage_path: Path) -> None:
        self._storage_path = storage_path
        self._lock = threading.RLock()
        self._chats: Dict[str, Chat] = {}
        self._load()

    # ------------------------------------------------------------------
    # Persistence helpers
    # ------------------------------------------------------------------
    def _load(self) -> None:
        self._storage_path.parent.mkdir(parents=True, exist_ok=True)
        if not self._storage_path.exists():
            self._storage_path.write_text("{}", encoding="utf-8")
            return

        raw = self._storage_path.read_text(encoding="utf-8") or "{}"
        try:
            data = json.loads(raw)
        except json.JSONDecodeError:
            data = {}
        self._chats = {chat_id: Chat.model_validate(value) for chat_id, value in data.items()}

    def _persist(self) -> None:
        payload = {chat_id: chat.model_dump() for chat_id, chat in self._chats.items()}
        self._storage_path.parent.mkdir(parents=True, exist_ok=True)
        self._storage_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    # ------------------------------------------------------------------
    # CRUD operations
    # ------------------------------------------------------------------
    def list_chats(self) -> Iterable[Chat]:
        with self._lock:
            return [
                chat.model_copy(deep=True)
                for chat in sorted(
                    self._chats.values(), key=lambda item: item.updated_at, reverse=True
                )
            ]

    def get_chat(self, chat_id: str) -> Optional[Chat]:
        with self._lock:
            chat = self._chats.get(chat_id)
            return chat.model_copy(deep=True) if chat else None

    def create_chat(self, form: ChatCreate) -> Chat:
        with self._lock:
            title = form.title or "New Chat"
            messages = [self._message_from_create(msg) for msg in form.messages or []]
            chat = Chat(title=title, messages=messages)
            self._chats[chat.id] = chat
            self._persist()
            return chat.model_copy(deep=True)

    def update_chat(self, chat_id: str, form: ChatUpdate) -> Optional[Chat]:
        with self._lock:
            chat = self._chats.get(chat_id)
            if not chat:
                return None

            if form.title is not None:
                chat.title = form.title
            if form.messages is not None:
                chat.messages = [self._message_from_create(msg) for msg in form.messages]
            chat.updated_at = datetime.utcnow().timestamp()
            self._chats[chat_id] = chat
            self._persist()
            return chat.model_copy(deep=True)

    def delete_chat(self, chat_id: str) -> bool:
        with self._lock:
            if chat_id in self._chats:
                del self._chats[chat_id]
                self._persist()
                return True
            return False

    def add_message(self, chat_id: str, form: MessageCreate) -> Optional[Message]:
        with self._lock:
            chat = self._chats.get(chat_id)
            if not chat:
                return None

            message = self._message_from_create(form)
            chat.messages.append(message)
            chat.updated_at = datetime.utcnow().timestamp()
            self._chats[chat_id] = chat
            self._persist()
            return message.model_copy(deep=True)

    @staticmethod
    def _message_from_create(form: MessageCreate) -> Message:
        return Message(role=form.role, content=form.content)


_store: ChatStore | None = None
_lock = threading.Lock()


def get_chat_store() -> ChatStore:
    global _store
    if _store is None:
        with _lock:
            if _store is None:
                _store = ChatStore(CHAT_STORAGE_PATH)
    return _store


def shutdown_chat_store() -> None:
    global _store
    with _lock:
        _store = None
