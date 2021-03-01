from typing import Dict

from fastapi.testclient import TestClient

from app.core.config import settings


def test_get_tokens(client: TestClient) -> None:
    login_data = {
        "username": settings.FIRST_SUPERUSER,
        "password": settings.FIRST_SUPERUSER_PASSWORD,
    }
    r = client.post(f"{settings.API_V1_STR}/login/access-token", data=login_data)
    tokens = r.json()
    assert r.status_code == 200
    assert "access_token" in tokens
    assert "refresh_token" in tokens
    assert tokens["access_token"]
    assert tokens["refresh_token"]


def test_use_access_token(client: TestClient, superuser_token_headers: Dict[str, str]) -> None:
    r = client.post(
        f"{settings.API_V1_STR}/login/test-token",
        headers=superuser_token_headers,
    )
    result = r.json()
    assert r.status_code == 200
    assert "email" in result


def test_use_refresh_token(client: TestClient, superuser_refresh_token_headers: Dict[str, str]) -> None:
    r = client.post(
        f"{settings.API_V1_STR}/login/refresh-token",
        headers=superuser_refresh_token_headers,
    )
    tokens = r.json()
    assert r.status_code == 200
    assert "access_token" in tokens
    assert "refresh_token" in tokens
    assert tokens["access_token"]
    assert tokens["refresh_token"]
