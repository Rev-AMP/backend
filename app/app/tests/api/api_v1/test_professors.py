from typing import Dict

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.core.config import settings
from app.schemas import AdminPermissions
from app.tests.utils.user import authentication_token_from_email, create_random_user


def test_get_professors_superuser(client: TestClient, superuser_token_headers: Dict[str, str], db: Session) -> None:
    create_random_user(db, type="professor")
    create_random_user(db, type="professor")
    r = client.get(
        f"{settings.API_V1_STR}/professors/",
        headers=superuser_token_headers,
    )
    assert r.status_code == 200
    all_professors = r.json()
    assert len(all_professors) >= 2
    for professor in all_professors:
        assert "user_id" in professor


def test_get_professors_admin_with_perms(client: TestClient, db: Session) -> None:
    create_random_user(db, type="professor")
    create_random_user(db, type="professor")
    admin_perms = AdminPermissions(0)
    admin_perms["professor"] = True
    admin_with_perms = create_random_user(db, type="admin", permissions=admin_perms.permissions)
    r = client.get(
        f"{settings.API_V1_STR}/professors/",
        headers=authentication_token_from_email(client=client, email=admin_with_perms.email, db=db),
    )
    assert r.status_code == 200
    all_professors = r.json()
    assert len(all_professors) > 2
    for professor in all_professors:
        assert "user_id" in professor


def test_get_professors_normal_user(client: TestClient, normal_user_token_headers: Dict[str, str], db: Session) -> None:
    create_random_user(db, type="professor")
    create_random_user(db, type="professor")
    r = client.get(
        f"{settings.API_V1_STR}/professors/",
        headers=normal_user_token_headers,
    )
    assert r.status_code == 403


def test_get_professor_me_superuser(client: TestClient, superuser_token_headers: Dict[str, str], db: Session) -> None:
    r = client.get(
        f"{settings.API_V1_STR}/professors/me",
        headers=superuser_token_headers,
    )
    assert r.status_code == 403


def test_get_professor_me_normal_professor(client: TestClient, db: Session) -> None:
    professor = create_random_user(db, type="professor")
    r = client.get(
        f"{settings.API_V1_STR}/professors/me",
        headers=authentication_token_from_email(client=client, email=professor.email, db=db),
    )
    assert r.status_code == 200
    fetched_professor = r.json()
    assert fetched_professor["user_id"] == professor.id


def test_get_professor_me_normal_user(
    client: TestClient, normal_user_token_headers: Dict[str, str], db: Session
) -> None:
    r = client.get(
        f"{settings.API_V1_STR}/professors/me",
        headers=normal_user_token_headers,
    )
    assert r.status_code == 403


def test_read_professor_by_id_superuser(
    client: TestClient, superuser_token_headers: Dict[str, str], db: Session
) -> None:
    professor = create_random_user(db, type="professor")
    r = client.get(
        f"{settings.API_V1_STR}/professors/{professor.id}",
        headers=superuser_token_headers,
    )
    assert r.status_code == 200
    fetched_professor = r.json()
    assert fetched_professor["user_id"] == professor.id


def test_read_professor_by_id_superuser_nonexistent_professor(
    client: TestClient, superuser_token_headers: Dict[str, str], db: Session
) -> None:
    user = create_random_user(db, type="student")
    r = client.get(
        f"{settings.API_V1_STR}/professors/{user.id}",
        headers=superuser_token_headers,
    )
    assert r.status_code == 404


def test_read_professor_by_id_admin_with_permissions(client: TestClient, db: Session) -> None:
    professor = create_random_user(db, type="professor")
    admin_perms = AdminPermissions(0)
    admin_perms["professor"] = True
    admin_with_perms = create_random_user(db, type="admin", permissions=admin_perms.permissions)
    r = client.get(
        f"{settings.API_V1_STR}/professors/{professor.id}",
        headers=authentication_token_from_email(client=client, email=admin_with_perms.email, db=db),
    )
    assert r.status_code == 200
    fetched_professor = r.json()
    assert fetched_professor["user_id"] == professor.id


def test_read_professor_by_id_professor(client: TestClient, db: Session) -> None:
    professor = create_random_user(db, type="professor")
    r = client.get(
        f"{settings.API_V1_STR}/professors/{professor.id}",
        headers=authentication_token_from_email(client=client, email=professor.email, db=db),
    )
    assert r.status_code == 200


def test_read_professor_by_id_normal_professor_fetch_self(client: TestClient, db: Session) -> None:
    professor = create_random_user(db, type="professor")
    r = client.get(
        f"{settings.API_V1_STR}/professors/{professor.id}",
        headers=authentication_token_from_email(client=client, email=professor.email, db=db),
    )
    assert r.status_code == 200
    fetched_professor = r.json()
    assert fetched_professor["user_id"] == professor.id


def test_read_professor_by_id_normal_user(
    client: TestClient, normal_user_token_headers: Dict[str, str], db: Session
) -> None:
    professor = create_random_user(db, type="professor")
    r = client.get(
        f"{settings.API_V1_STR}/professors/{professor.id}",
        headers=normal_user_token_headers,
    )
    assert r.status_code == 403


def test_update_professor_superuser(client: TestClient, superuser_token_headers: Dict[str, str], db: Session) -> None:
    professor = create_random_user(db, type="professor")
    r = client.put(f"{settings.API_V1_STR}/professors/{professor.id}", headers=superuser_token_headers, json={})
    assert r.status_code == 200
    updated_professor = r.json()
    assert professor.id == updated_professor["user_id"]
