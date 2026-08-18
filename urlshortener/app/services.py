import secrets
from datetime import datetime, timezone

from fastapi import HTTPException
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from .models import ShortLink


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


def generate_code() -> str:
    return secrets.token_urlsafe(6).replace("-", "").replace("_", "")[:8]


def create_link(session: Session, url: str, custom_code: str | None, expires_at: datetime | None) -> ShortLink:
    if expires_at and expires_at <= utc_now():
        raise HTTPException(status_code=422, detail="expires_at must be in the future")
    for _ in range(5):
        code = custom_code or generate_code()
        if session.get(ShortLink, code):
            if custom_code:
                raise HTTPException(status_code=409, detail="custom_code is already in use")
            continue
        link = ShortLink(code=code, destination_url=url, expires_at=expires_at)
        session.add(link)
        try:
            session.commit()
            session.refresh(link)
            return link
        except IntegrityError:
            session.rollback()
            if custom_code:
                raise HTTPException(status_code=409, detail="custom_code is already in use")
    raise HTTPException(status_code=503, detail="could not allocate a unique code")


def resolve_link(session: Session, code: str) -> ShortLink:
    link = session.get(ShortLink, code)
    if not link:
        raise HTTPException(status_code=404, detail="short link not found")
    if link.expires_at and link.expires_at.replace(tzinfo=timezone.utc) <= utc_now():
        raise HTTPException(status_code=410, detail="short link has expired")
    link.click_count += 1
    session.commit()
    session.refresh(link)
    return link


def get_analytics(session: Session, code: str) -> ShortLink:
    link = session.get(ShortLink, code)
    if not link:
        raise HTTPException(status_code=404, detail="short link not found")
    return link
