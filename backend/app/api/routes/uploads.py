import os
import re
import uuid
from datetime import datetime, timedelta, timezone
from typing import Any

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.api.tenant import creation_tenant, require_same_tenant
from app.db.session import get_db
from app.models.user import User

router = APIRouter()
UPLOAD_DIR = os.path.join(os.getcwd(), "static", "uploads")
MAX_IMAGE_BYTES = 10 * 1024 * 1024
SESSION_LIFETIME = timedelta(minutes=10)
os.makedirs(UPLOAD_DIR, exist_ok=True)

# QR links are bearer capabilities. They expire and can be redeemed once.
upload_sessions: dict[str, dict[str, Any]] = {}


class SessionResponse(BaseModel):
    session_id: str
    status: str
    photo_url: str | None = None
    created_at: str


def validate_photo_url(url: str | None, empresa_id: int, existing_url: str | None = None) -> None:
    pattern = rf"/static/uploads/{empresa_id}/[0-9a-f]{{32}}\.(?:jpg|png|webp)"
    if url and url != existing_url and re.fullmatch(pattern, url) is None:
        raise HTTPException(400, "La fotografía no pertenece a la empresa")


def _image_extension(data: bytes) -> str:
    if data.startswith(b"\xff\xd8\xff"):
        return ".jpg"
    if data.startswith(b"\x89PNG\r\n\x1a\n"):
        return ".png"
    if data[:4] == b"RIFF" and data[8:12] == b"WEBP":
        return ".webp"
    raise HTTPException(400, "Solo se admiten imágenes JPEG, PNG o WebP")


async def _save_image(file: UploadFile, empresa_id: int) -> str:
    contents = await file.read(MAX_IMAGE_BYTES + 1)
    if len(contents) > MAX_IMAGE_BYTES:
        raise HTTPException(413, "La imagen supera el límite de 10 MB")
    extension = _image_extension(contents)
    directory = os.path.join(UPLOAD_DIR, str(empresa_id))
    os.makedirs(directory, exist_ok=True)
    filename = f"{uuid.uuid4().hex}{extension}"
    with open(os.path.join(directory, filename), "wb") as output:
        output.write(contents)
    return f"/static/uploads/{empresa_id}/{filename}"


def _session(session_id: str) -> dict[str, Any]:
    session = upload_sessions.get(session_id)
    if session is None:
        raise HTTPException(404, "Sesión de captura no encontrada")
    if datetime.now(timezone.utc) >= session["expires_at"]:
        upload_sessions.pop(session_id, None)
        raise HTTPException(410, "Sesión de captura expirada")
    return session


@router.post("/file")
async def upload_file(
    file: UploadFile = File(...),
    empresa_id: int | None = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    target = creation_tenant(db, current_user, empresa_id)
    url = await _save_image(file, target)
    return {"url": url, "filename": url.rsplit("/", 1)[-1]}


@router.post("/session/create", response_model=SessionResponse)
def create_upload_session(
    empresa_id: int | None = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    target = creation_tenant(db, current_user, empresa_id)
    session_id = uuid.uuid4().hex
    now = datetime.now(timezone.utc)
    for stale_id, stale_session in list(upload_sessions.items()):
        if now >= stale_session["expires_at"]:
            upload_sessions.pop(stale_id, None)
    session = {
        "session_id": session_id,
        "status": "PENDING",
        "photo_url": None,
        "created_at": now.isoformat(),
        "expires_at": now + SESSION_LIFETIME,
        "empresa_id": target,
        "creator_id": current_user.id,
    }
    upload_sessions[session_id] = session
    return session


@router.get("/session/{session_id}", response_model=SessionResponse)
def get_upload_session(session_id: str, current_user: User = Depends(get_current_user)):
    session = _session(session_id)
    require_same_tenant(current_user, session["empresa_id"])
    if current_user.id != session["creator_id"]:
        raise HTTPException(404, "Sesión de captura no encontrada")
    return session


@router.post("/session/{session_id}/upload")
async def upload_session_photo(session_id: str, file: UploadFile = File(...)):
    session = _session(session_id)
    if session["status"] != "PENDING":
        raise HTTPException(409, "La sesión de captura ya se utilizó")
    session["status"] = "UPLOADING"
    try:
        url = await _save_image(file, session["empresa_id"])
    except Exception:
        session["status"] = "PENDING"
        raise
    session["status"] = "COMPLETED"
    session["photo_url"] = url
    return {"status": "COMPLETED", "photo_url": url}
