from typing import Dict

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.core.config import settings
from app.tests.utils.user import authentication_token_from_email, create_random_user


def test_get_admins_superuser(client: TestClient, superuser_token_headers: Dict[str, str], db: Session) -> None:
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


def test_get_admins_normal_admin(client: TestClient, admin_user_token_headers: Dict[str, str], db: Session) -> None:
    create_random_user(db, type="admin")
    create_random_user(db, type="admin")
    r = client.get(
        f"{settings.API_V1_STR}/admins/",
        headers=admin_user_token_headers,
    )
    assert r.status_code == 403


def test_get_admins_admin_with_perms(client: TestClient, db: Session) -> None:
    create_random_user(db, type="admin")
    create_random_user(db, type="admin")
    admin_with_perms = create_random_user(db, type="admin", permissions=2)
    r = client.get(
        f"{settings.API_V1_STR}/admins/",
        headers=authentication_token_from_email(client=client, email=admin_with_perms.email, db=db),
    )
    assert r.status_code == 200
    all_admins = r.json()
    assert len(all_admins) > 2
    for admin in all_admins:
        assert "permissions" in admin


def test_get_admins_normal_user(client: TestClient, normal_user_token_headers: Dict[str, str], db: Session) -> None:
    create_random_user(db, type="admin")
    create_random_user(db, type="admin")
    r = client.get(
        f"{settings.API_V1_STR}/admins/",
        headers=normal_user_token_headers,
    )
    assert r.status_code == 403


def test_get_admin_me_superuser(client: TestClient, superuser_token_headers: Dict[str, str], db: Session) -> None:
    r = client.get(
        f"{settings.API_V1_STR}/admins/me",
        headers=superuser_token_headers,
    )
    assert r.status_code == 200
    admin = r.json()
    assert admin["user_id"] == 1
    assert admin["permissions"] == -1


def test_get_admin_me_normal_admin(client: TestClient, db: Session) -> None:
    admin = create_random_user(db, type="admin")
    r = client.get(
        f"{settings.API_V1_STR}/admins/me",
        headers=authentication_token_from_email(client=client, email=admin.email, db=db),
    )
    assert r.status_code == 200
    fetched_admin = r.json()
    assert fetched_admin["user_id"] == admin.id
    assert fetched_admin["permissions"] == 0


def test_get_admin_me_normal_user(client: TestClient, normal_user_token_headers: Dict[str, str], db: Session) -> None:
    r = client.get(
        f"{settings.API_V1_STR}/admins/me",
        headers=normal_user_token_headers,
    )
    assert r.status_code == 403


def test_read_admin_by_id_superuser(client: TestClient, superuser_token_headers: Dict[str, str], db: Session) -> None:
    admin = create_random_user(db, type="admin")
    r = client.get(
        f"{settings.API_V1_STR}/admins/{admin.id}",
        headers=superuser_token_headers,
    )
    assert r.status_code == 200
    fetched_admin = r.json()
    assert fetched_admin["user_id"] == admin.id
    assert fetched_admin["permissions"] == 0


def test_read_admin_by_id_superuser_nonexistent_admin(
    client: TestClient, superuser_token_headers: Dict[str, str], db: Session
) -> None:
    user = create_random_user(db, type="student")
    r = client.get(
        f"{settings.API_V1_STR}/admins/{user.id}",
        headers=superuser_token_headers,
    )
    assert r.status_code == 404


def test_read_admin_by_id_admin_with_permissions(client: TestClient, db: Session) -> None:
    admin = create_random_user(db, type="admin")
    admin_with_perms = create_random_user(db, type="admin", permissions=2)
    r = client.get(
        f"{settings.API_V1_STR}/admins/{admin.id}",
        headers=authentication_token_from_email(client=client, email=admin_with_perms.email, db=db),
    )
    assert r.status_code == 200
    fetched_admin = r.json()
    assert fetched_admin["user_id"] == admin.id
    assert fetched_admin["permissions"] == 0


def test_read_admin_by_id_normal_admin(
    client: TestClient, admin_user_token_headers: Dict[str, str], db: Session
) -> None:
    admin = create_random_user(db, type="admin")
    r = client.get(
        f"{settings.API_V1_STR}/admins/{admin.id}",
        headers=admin_user_token_headers,
    )
    assert r.status_code == 403


def test_read_admin_by_id_normal_admin_fetch_self(client: TestClient, db: Session) -> None:
    admin = create_random_user(db, type="admin")
    r = client.get(
        f"{settings.API_V1_STR}/admins/{admin.id}",
        headers=authentication_token_from_email(client=client, email=admin.email, db=db),
    )
    assert r.status_code == 200
    fetched_admin = r.json()
    assert fetched_admin["user_id"] == admin.id
    assert fetched_admin["permissions"] == 0


def test_read_admin_by_id_normal_user(
    client: TestClient, normal_user_token_headers: Dict[str, str], db: Session
) -> None:
    admin = create_random_user(db, type="admin")
    r = client.get(
        f"{settings.API_V1_STR}/admins/{admin.id}",
        headers=normal_user_token_headers,
    )
    assert r.status_code == 403


def test_update_admin(client: TestClient, superuser_token_headers: Dict[str, str], db: Session) -> None:
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


def test_update_admin_nonadmin(client: TestClient, superuser_token_headers: Dict[str, str], db: Session) -> None:
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
    assert "user_id" not in updated_admin
