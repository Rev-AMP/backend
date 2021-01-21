from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app import crud
from app.core.config import settings
from app.tests.utils.user import create_random_user


def test_get_existing_admin(client: TestClient, superuser_token_headers: dict, db: Session) -> None:
    r = client.get(
        f"{settings.API_V1_STR}/admins/",
        headers=superuser_token_headers,
    )
    assert 200 <= r.status_code < 300
    api_user = r.json()
    existing_user = crud.admin.get(db, id=1)
    assert existing_user
    assert existing_user.user_id == api_user["user_id"]
    assert existing_user.permissions == api_user["permissions"]


def test_create_admin_existing_id(client: TestClient, superuser_token_headers: dict, db: Session) -> None:
    user = create_random_user(db, type="admin")
    admin_id = user.id
    data = {"user_id": admin_id, "permissions": 0}
    r = client.post(
        f"{settings.API_V1_STR}/admins/",
        headers=superuser_token_headers,
        json=data,
    )
    created_user = r.json()
    assert 400 <= r.status_code < 500
    assert "user_id" not in created_user


def test_create_admin_existing_nonadmin(client: TestClient, superuser_token_headers: dict, db: Session) -> None:
    user = create_random_user(db, type="professor")
    admin_id = user.id
    data = {"user_id": admin_id, "permissions": 0}
    r = client.post(
        f"{settings.API_V1_STR}/admins/",
        headers=superuser_token_headers,
        json=data,
    )
    created_admin = r.json()
    db.refresh(user)
    assert 200 <= r.status_code < 300
    assert user
    assert crud.user.check_admin(user)
    assert "user_id" in created_admin
    assert "permissions" in created_admin


def test_create_admin_existing_student(client: TestClient, superuser_token_headers: dict, db: Session) -> None:
    user = create_random_user(db, type="student")
    admin_id = user.id
    data = {"user_id": admin_id, "permissions": 0}
    r = client.post(
        f"{settings.API_V1_STR}/admins/",
        headers=superuser_token_headers,
        json=data,
    )
    created_admin = r.json()
    db.refresh(user)
    assert 400 <= r.status_code < 500
    assert user
    assert not crud.user.check_admin(user)
    assert "user_id" not in created_admin


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
    assert 200 <= r.status_code < 300
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
    assert 400 <= r.status_code < 500
    db.refresh(user)
    assert user
    assert not crud.user.check_admin(user)
    assert 'user_id' not in updated_admin


def test_remove_admin(client: TestClient, superuser_token_headers: dict, db: Session) -> None:
    user = create_random_user(db, type="admin")
    admin_id = user.id
    data = {"user_id": admin_id}
    r = client.delete(
        f"{settings.API_V1_STR}/admins/",
        headers=superuser_token_headers,
        json=data,
    )
    db.refresh(user)
    assert 200 <= r.status_code < 300
    assert user
    assert not crud.user.check_admin(user)
    assert not crud.admin.get(db, id=admin_id)


def test_remove_admin_nonadmin(client: TestClient, superuser_token_headers: dict, db: Session) -> None:
    user = create_random_user(db, type="student")
    admin_id = user.id
    data = {"user_id": admin_id}
    r = client.delete(
        f"{settings.API_V1_STR}/admins/",
        headers=superuser_token_headers,
        json=data,
    )
    db.refresh(user)
    assert 400 <= r.status_code < 500
    assert user
    assert not crud.user.check_admin(user)


def test_remove_admin_nonuser(client: TestClient, superuser_token_headers: dict, db: Session) -> None:
    user = create_random_user(db, type="student")
    admin_id = user.id
    crud.user.remove(db, id=admin_id)
    assert not crud.user.get(db, id=admin_id)
    data = {"user_id": admin_id}
    r = client.delete(
        f"{settings.API_V1_STR}/admins/",
        headers=superuser_token_headers,
        json=data,
    )
    assert 400 <= r.status_code < 500
