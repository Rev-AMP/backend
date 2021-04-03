from typing import Dict

from fastapi.testclient import TestClient

from app.core.config import settings
from app.core.security import create_token
from app.tests.utils.utils import random_email, random_password


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
    assert "expiry" in tokens
    assert tokens["access_token"]
    assert tokens["refresh_token"]
    assert tokens["expiry"]


def test_invalid_credentials(client: TestClient) -> None:
    login_data = {
        "username": random_email(),
        "password": random_password(),
    }
    r = client.post(f"{settings.API_V1_STR}/login/access-token", data=login_data)
    assert r.status_code == 401


def test_use_access_token(client: TestClient, superuser_token_headers: Dict[str, str]) -> None:
    r = client.post(
        f"{settings.API_V1_STR}/login/test-token",
        headers=superuser_token_headers,
    )
    result = r.json()
    assert r.status_code == 200
    assert "email" in result


def test_nonexistent_user(client: TestClient, superuser_token_headers: Dict[str, str]) -> None:
    token = create_token("-1").access_token
    r = client.post(
        f"{settings.API_V1_STR}/login/test-token",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert r.status_code == 404


def test_nonexistent_user_refresh(client: TestClient, superuser_token_headers: Dict[str, str]) -> None:
    token = create_token("-1").refresh_token
    r = client.post(
        f"{settings.API_V1_STR}/login/refresh-token",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert r.status_code == 404


def test_use_refresh_token(client: TestClient, superuser_refresh_token_headers: Dict[str, str]) -> None:
    r = client.post(
        f"{settings.API_V1_STR}/login/refresh-token",
        headers=superuser_refresh_token_headers,
    )
    tokens = r.json()
    assert r.status_code == 200
    assert "access_token" in tokens
    assert "refresh_token" in tokens
    assert "expiry" in tokens
    assert tokens["access_token"]
    assert tokens["refresh_token"]
    assert tokens["expiry"]


def test_password_reset(client: TestClient) -> None:
    r = client.post(
        f"{settings.API_V1_STR}/password-recovery/{settings.FIRST_SUPERUSER}",
    )
    assert r.status_code == 200


def test_password_reset_nonexistent_user(client: TestClient) -> None:
    r = client.post(
        f"{settings.API_V1_STR}/password-recovery/{random_email()}",
    )
    assert r.status_code == 404


def test_invalid_access_token(client: TestClient) -> None:
    r = client.post(f"{settings.API_V1_STR}/login/test-token", headers={"Authorization": "Bearer"})
    assert r.status_code == 403


def test_invalid_refresh_token(client: TestClient) -> None:
    r = client.post(f"{settings.API_V1_STR}/login/refresh-token", headers={"Authorization": "Bearer"})
    assert r.status_code == 403


def test_refresh_for_access(client: TestClient) -> None:
    token = create_token("0").refresh_token
    r = client.post(f"{settings.API_V1_STR}/login/test-token", headers={"Authorization": f"Bearer {token}"})
    assert r.status_code == 400


def test_access_for_refresh(client: TestClient) -> None:
    token = create_token("0").access_token
    r = client.post(f"{settings.API_V1_STR}/login/refresh-token", headers={"Authorization": f"Bearer {token}"})
    assert r.status_code == 400
