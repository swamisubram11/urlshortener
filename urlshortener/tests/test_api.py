from datetime import datetime, timedelta, timezone


def test_create_redirect_and_analytics(client):
    created = client.post("/api/v1/links", json={"url": "https://example.com/path", "custom_code": "demo1"})
    assert created.status_code == 201
    assert created.json()["code"] == "demo1"
    redirected = client.get("/demo1", follow_redirects=False)
    assert redirected.status_code == 307
    assert redirected.headers["location"] == "https://example.com/path"
    analytics = client.get("/api/v1/links/demo1/analytics")
    assert analytics.status_code == 200
    assert analytics.json()["click_count"] == 1


def test_duplicate_custom_code_is_conflict(client):
    payload = {"url": "https://example.com", "custom_code": "same"}
    assert client.post("/api/v1/links", json=payload).status_code == 201
    assert client.post("/api/v1/links", json=payload).status_code == 409


def test_expired_link_returns_validation_error(client):
    expired = (datetime.now(timezone.utc) - timedelta(minutes=1)).isoformat()
    response = client.post("/api/v1/links", json={"url": "https://example.com", "custom_code": "old1", "expires_at": expired})
    assert response.status_code == 422
