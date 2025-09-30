"""Pydantic models used by the chat API."""

from __future__ import annotations

from datetime import datetime
from typing import List, Optional
from uuid import uuid4

from pydantic import BaseModel, Field


class Message(BaseModel):
    id: str = Field(default_factory=lambda: uuid4().hex)
    role: str
    content: str
    created_at: float = Field(default_factory=lambda: datetime.utcnow().timestamp())


class MessageCreate(BaseModel):
    role: str
    content: str


class Chat(BaseModel):
    id: str = Field(default_factory=lambda: uuid4().hex)
    title: str
    messages: List[Message] = Field(default_factory=list)
    created_at: float = Field(default_factory=lambda: datetime.utcnow().timestamp())
    updated_at: float = Field(default_factory=lambda: datetime.utcnow().timestamp())


class ChatCreate(BaseModel):
    title: Optional[str] = None
    messages: Optional[List[MessageCreate]] = None


class ChatUpdate(BaseModel):
    title: Optional[str] = None
    messages: Optional[List[MessageCreate]] = None
