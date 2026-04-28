"""Pydantic models for Notice Board operations."""

from pydantic import BaseModel
from typing import Optional


class NoticeCreate(BaseModel):
    title: str
    message: str


class NoticeResponse(BaseModel):
    id: str
    title: str
    message: str
    posted_by: str
    created_at: str
