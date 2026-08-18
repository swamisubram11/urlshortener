from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI, Request
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session

from .database import Base, engine, get_session
from .schemas import AnalyticsResponse, ShortenRequest, ShortenResponse
from .services import create_link, get_analytics, resolve_link


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(title="URL Shortener", version="1.0.0", lifespan=lifespan)


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/api/v1/links", response_model=ShortenResponse, status_code=201)
def shorten(body: ShortenRequest, request: Request, session: Session = Depends(get_session)):
    link = create_link(session, str(body.url), body.custom_code, body.expires_at)
    return ShortenResponse(code=link.code, short_url=str(request.base_url) + link.code, destination_url=link.destination_url, expires_at=link.expires_at)


@app.get("/{code}", status_code=307)
def redirect(code: str, session: Session = Depends(get_session)):
    link = resolve_link(session, code)
    return RedirectResponse(link.destination_url, status_code=307)


@app.get("/api/v1/links/{code}/analytics", response_model=AnalyticsResponse)
def analytics(code: str, session: Session = Depends(get_session)):
    return get_analytics(session, code)
