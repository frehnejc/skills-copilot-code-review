"""Announcement endpoints for the High School Management System API."""

from datetime import date
from typing import Any, Dict, List, Optional
from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel

from ..database import announcements_collection
from .auth import require_authenticated_user

router = APIRouter(prefix="/announcements", tags=["announcements"])


class AnnouncementInput(BaseModel):
    message: str
    expiration_date: date
    start_date: Optional[date] = None


def validate_announcement(announcement: AnnouncementInput) -> None:
    if not announcement.message.strip():
        raise HTTPException(status_code=422, detail="Message is required")
    if announcement.start_date and announcement.expiration_date < announcement.start_date:
        raise HTTPException(
            status_code=422,
            detail="Expiration date must be on or after the start date",
        )


def serialize_announcement(document: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "id": str(document["_id"]),
        "message": document["message"],
        "start_date": document.get("start_date"),
        "expiration_date": document["expiration_date"],
    }


@router.get("", response_model=List[Dict[str, Any]])
def get_active_announcements() -> List[Dict[str, Any]]:
    """List announcements whose configured date range includes today."""
    today = date.today().isoformat()
    query = {
        "expiration_date": {"$gte": today},
        "$or": [
            {"start_date": None},
            {"start_date": {"$exists": False}},
            {"start_date": {"$lte": today}},
        ],
    }
    return [serialize_announcement(item) for item in announcements_collection.find(query)]


@router.get("/manage", response_model=List[Dict[str, Any]])
def get_all_announcements(
    _: Dict[str, Any] = Depends(require_authenticated_user),
) -> List[Dict[str, Any]]:
    """List every announcement for signed-in users, including inactive items."""
    items = announcements_collection.find({}).sort("expiration_date", -1)
    return [serialize_announcement(item) for item in items]


@router.post("", response_model=Dict[str, Any], status_code=status.HTTP_201_CREATED)
def create_announcement(
    announcement: AnnouncementInput,
    _: Dict[str, Any] = Depends(require_authenticated_user),
) -> Dict[str, Any]:
    """Create an announcement. Requires a signed-in user."""
    validate_announcement(announcement)
    document = {
        "_id": str(uuid4()),
        "message": announcement.message.strip(),
        "start_date": announcement.start_date.isoformat() if announcement.start_date else None,
        "expiration_date": announcement.expiration_date.isoformat(),
    }
    announcements_collection.insert_one(document)
    return serialize_announcement(document)


@router.put("/{announcement_id}", response_model=Dict[str, Any])
def update_announcement(
    announcement_id: str,
    announcement: AnnouncementInput,
    _: Dict[str, Any] = Depends(require_authenticated_user),
) -> Dict[str, Any]:
    """Update an announcement. Requires a signed-in user."""
    validate_announcement(announcement)
    changes = {
        "message": announcement.message.strip(),
        "start_date": announcement.start_date.isoformat() if announcement.start_date else None,
        "expiration_date": announcement.expiration_date.isoformat(),
    }
    result = announcements_collection.update_one({"_id": announcement_id}, {"$set": changes})
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Announcement not found")
    return serialize_announcement({"_id": announcement_id, **changes})


@router.delete("/{announcement_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_announcement(
    announcement_id: str,
    _: Dict[str, Any] = Depends(require_authenticated_user),
) -> None:
    """Delete an announcement. Requires a signed-in user."""
    result = announcements_collection.delete_one({"_id": announcement_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Announcement not found")