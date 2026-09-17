"""
Authentication endpoints for the High School Management System API
"""

from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
import secrets
from typing import Dict, Any

from ..database import teachers_collection, verify_password

router = APIRouter(
    prefix="/auth",
    tags=["auth"]
)

security = HTTPBearer(auto_error=False)
sessions: Dict[str, str] = {}


def require_authenticated_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
) -> Dict[str, Any]:
    """Return the teacher associated with a valid login session."""
    token = credentials.credentials if credentials else None
    username = sessions.get(token) if token else None
    teacher = teachers_collection.find_one({"_id": username}) if username else None

    if not teacher:
        raise HTTPException(status_code=401, detail="Authentication required")

    return teacher


@router.post("/login")
def login(username: str, password: str) -> Dict[str, Any]:
    """Login a teacher account"""
    # Find the teacher in the database
    teacher = teachers_collection.find_one({"_id": username})

    # Verify password using Argon2 verifier from database.py
    if not teacher or not verify_password(teacher.get("password", ""), password):
        raise HTTPException(
            status_code=401, detail="Invalid username or password")

    session_token = secrets.token_urlsafe(32)
    sessions[session_token] = username

    # Return teacher information (excluding password)
    return {
        "username": teacher["username"],
        "display_name": teacher["display_name"],
        "role": teacher["role"],
        "session_token": session_token
    }


@router.get("/check-session")
def check_session(
    teacher: Dict[str, Any] = Depends(require_authenticated_user),
) -> Dict[str, Any]:
    """Check whether the supplied bearer session is valid."""

    return {
        "username": teacher["username"],
        "display_name": teacher["display_name"],
        "role": teacher["role"]
    }


@router.post("/logout", status_code=204)
def logout(
    credentials: HTTPAuthorizationCredentials = Depends(security),
) -> None:
    """Invalidate the supplied login session."""
    if credentials:
        sessions.pop(credentials.credentials, None)
