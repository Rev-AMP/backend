from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.core.config import settings
from app.tests.utils.user import create_random_user


def test_get_existing_admin(client: TestClient, superuser_token_headers: dict, db: Session) -> None:
    create_random_user(db, type="admin")
    create_random_user(db, type="admin")
    r = client.get(
        f"{settings.API_V1_STR}/admins/",
        headers=superuser_token_headers,
    )
    assert r.status_code == 200
    all_admins = r.json()
    assert len(all_admins) > 2
    for admin in all_admins:
        assert "permissions" in admin


def test_get_existing_admin_me(client: TestClient, superuser_token_headers: dict, db: Session) -> None:
    r = client.get(
        f"{settings.API_V1_STR}/admins/me",
        headers=superuser_token_headers,
    )
    assert r.status_code == 200
    admin = r.json()
    print(admin)
    assert admin['user_id'] == 1
    assert admin['permissions'] == -1


def test_update_admin(client: TestClient, superuser_token_headers: dict, db: Session) -> None:
    user = create_random_user(db, type="admin")
    admin_id = user.id
    data = {"user_id": admin_id, "permissions": 5}
    r = client.put(
        f"{settings.API_V1_STR}/admins/",
        headers=superuser_token_headers,
        json=data,
    )
    updated_admin = r.json()
    assert r.status_code == 200
    assert updated_admin["permissions"] == 5


def test_update_admin_nonadmin(client: TestClient, superuser_token_headers: dict, db: Session) -> None:
    user = create_random_user(db, type="student")
    admin_id = user.id
    data = {"user_id": admin_id, "permissions": 5}
    r = client.put(
        f"{settings.API_V1_STR}/admins/",
        headers=superuser_token_headers,
        json=data,
    )
    updated_admin = r.json()
    assert r.status_code == 404
    db.refresh(user)
    assert user
    assert not user.is_admin
    assert 'user_id' not in updated_admin
