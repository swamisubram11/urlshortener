from datetime import datetime

from pydantic import AnyHttpUrl, BaseModel, Field


class ShortenRequest(BaseModel):
    url: AnyHttpUrl
    custom_code: str | None = Field(default=None, pattern=r"^[A-Za-z0-9_-]{4,32}$")
    expires_at: datetime | None = None


class ShortenResponse(BaseModel):
    code: str
    short_url: str
    destination_url: str
    expires_at: datetime | None


class AnalyticsResponse(BaseModel):
    code: str
    destination_url: str
    click_count: int
    created_at: datetime
    expires_at: datetime | None
