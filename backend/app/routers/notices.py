"""Notices router — broadcast messages from admin to the notice board."""

from fastapi import APIRouter, HTTPException, status, Depends
from app.database import notices_collection
from app.models.notice import NoticeCreate, NoticeResponse
from app.utils.deps import require_admin
from bson import ObjectId
from datetime import datetime, timezone

router = APIRouter(prefix="/api/notices", tags=["Notices"])


def serialize_notice(notice: dict) -> dict:
    """Convert MongoDB document to response-friendly dict."""
    return {
        "id": str(notice["_id"]),
        "title": notice["title"],
        "message": notice["message"],
        "posted_by": notice.get("posted_by", ""),
        "created_at": notice["created_at"].isoformat() if isinstance(notice["created_at"], datetime) else str(notice["created_at"]),
    }


@router.get("/", response_model=list[NoticeResponse])
async def get_notices():
    """Get all notices (public)."""
    notices = await notices_collection.find().sort("created_at", -1).to_list(length=20)
    return [serialize_notice(n) for n in notices]


@router.post("/", response_model=NoticeResponse, status_code=status.HTTP_201_CREATED)
async def create_notice(notice: NoticeCreate, admin=Depends(require_admin)):
    """Post a new notice (Admin only)."""
    notice_doc = {
        "title": notice.title,
        "message": notice.message,
        "posted_by": str(admin["_id"]),
        "created_at": datetime.now(timezone.utc),
    }

    result = await notices_collection.insert_one(notice_doc)
    notice_doc["_id"] = result.inserted_id
    return serialize_notice(notice_doc)


@router.delete("/{notice_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_notice(notice_id: str, admin=Depends(require_admin)):
    """Delete a notice (Admin only)."""
    if not ObjectId.is_valid(notice_id):
        raise HTTPException(status_code=400, detail="Invalid notice ID")

    result = await notices_collection.delete_one({"_id": ObjectId(notice_id)})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Notice not found")
