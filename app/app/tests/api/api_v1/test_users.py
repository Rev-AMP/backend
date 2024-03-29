from os import remove
from os.path import isfile

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app import crud
from app.core.config import settings
from app.core.security import verify_password
from app.tests.utils.user import authentication_token_from_email, create_random_user
from app.tests.utils.utils import (
    compare_api_and_db_query_results,
    random_email,
    random_lower_string,
    random_password,
    to_json,
)
from app.utils import generate_uuid


def test_get_users_superuser_me(client: TestClient, superuser_token_headers: dict[str, str]) -> None:
    r = client.get(f"{settings.API_V1_STR}/users/me", headers=superuser_token_headers)
    current_user = r.json()
    assert current_user
    assert current_user["is_active"] is True
    assert current_user["type"] == "superuser"
    assert current_user["email"] == settings.FIRST_SUPERUSER


def test_get_users_normal_user_me(client: TestClient, normal_user_token_headers: dict[str, str]) -> None:
    r = client.get(f"{settings.API_V1_STR}/users/me", headers=normal_user_token_headers)
    current_user = r.json()
    assert current_user
    assert current_user["is_active"] is True
    assert current_user["type"] != "superuser"
    assert current_user["email"] == settings.EMAIL_TEST_USER


def test_create_user_new_email(client: TestClient, superuser_token_headers: dict, db: Session) -> None:
    username = random_email()
    password = random_password()
    data = {"email": username, "password": password, "type": "superuser"}
    r = client.post(
        f"{settings.API_V1_STR}/users/",
        headers=superuser_token_headers,
        json=data,
    )
    assert r.status_code == 200
    created_user = r.json()
    user = crud.user.get_by_email(db, email=username)
    assert user
    compare_api_and_db_query_results(api_result=created_user, db_dict=to_json(user))


def test_get_existing_user(client: TestClient, superuser_token_headers: dict, db: Session) -> None:
    user = create_random_user(db=db, type="superuser")
    assert user
    user_id = user.id
    r = client.get(
        f"{settings.API_V1_STR}/users/{user_id}",
        headers=superuser_token_headers,
    )
    assert r.status_code == 200
    api_user = r.json()
    compare_api_and_db_query_results(api_result=api_user, db_dict=to_json(user))


def test_create_user_existing_username(client: TestClient, superuser_token_headers: dict, db: Session) -> None:
    user = create_random_user(db=db, type="superuser")
    data = {"email": user.email, "password": random_password(), "type": "superuser"}
    r = client.post(
        f"{settings.API_V1_STR}/users/",
        headers=superuser_token_headers,
        json=data,
    )
    created_user = r.json()
    assert r.status_code == 409
    assert "_id" not in created_user


def test_create_user_by_normal_user(client: TestClient, normal_user_token_headers: dict[str, str]) -> None:
    username = random_email()
    password = random_password()
    data = {"email": username, "password": password, "type": "superuser"}
    r = client.post(
        f"{settings.API_V1_STR}/users/",
        headers=normal_user_token_headers,
        json=data,
    )
    assert r.status_code == 403


def test_create_superuser_by_superuser(client: TestClient, superuser_token_headers: dict[str, str]) -> None:
    username = random_email()
    password = random_password()
    data = {"email": username, "password": password, "type": "superuser"}
    r = client.post(
        f"{settings.API_V1_STR}/users/",
        headers=superuser_token_headers,
        json=data,
    )
    assert r.status_code == 200


def test_create_superuser_by_normal_admin(client: TestClient, admin_user_token_headers: dict[str, str]) -> None:
    username = random_email()
    password = random_password()
    data = {"email": username, "password": password, "type": "superuser"}
    r = client.post(
        f"{settings.API_V1_STR}/users/",
        headers=admin_user_token_headers,
        json=data,
    )
    assert r.status_code == 403


def test_create_superuser_by_normal_admin_with_user_perms(client: TestClient, db: Session) -> None:
    admin_user = create_random_user(db=db, type="admin", is_admin=True, permissions=1)
    username = random_email()
    password = random_password()
    data = {"email": username, "password": password, "type": "superuser"}
    r = client.post(
        f"{settings.API_V1_STR}/users/",
        headers=authentication_token_from_email(client=client, email=admin_user.email, db=db),
        json=data,
    )
    assert r.status_code == 403


def test_retrieve_users(client: TestClient, superuser_token_headers: dict, db: Session) -> None:
    create_random_user(db, type="superuser")
    create_random_user(db, type="superuser")

    r = client.get(f"{settings.API_V1_STR}/users/", headers=superuser_token_headers)
    all_users = r.json()

    assert len(all_users) > 1
    for item in all_users:
        assert "email" in item


def test_user_update_me(client: TestClient, db: Session) -> None:
    user = create_random_user(db, type="student")
    full_name = random_lower_string()
    email = random_email()
    password = random_password()
    data = {"full_name": full_name, "email": email, "password": password}
    r = client.put(
        f"{settings.API_V1_STR}/users/me",
        headers=authentication_token_from_email(client=client, email=user.email, db=db),
        json=data,
    )
    assert r.status_code == 200
    updated_user = r.json()
    db.refresh(user)
    compare_api_and_db_query_results(api_result=updated_user, db_dict=to_json(user))
    assert verify_password(password, user.hashed_password)


def test_read_user_self(client: TestClient, db: Session) -> None:
    user = create_random_user(db, type="student")
    r = client.get(
        f"{settings.API_V1_STR}/users/{user.id}",
        headers=authentication_token_from_email(client=client, email=user.email, db=db),
    )
    assert r.status_code == 200
    fetched_user = r.json()
    compare_api_and_db_query_results(api_result=fetched_user, db_dict=to_json(user))


def test_read_user_superuser(client: TestClient, superuser_token_headers: dict[str, str], db: Session) -> None:
    user = create_random_user(db, type="student")
    r = client.get(f"{settings.API_V1_STR}/users/{user.id}", headers=superuser_token_headers)
    assert r.status_code == 200
    fetched_user = r.json()
    compare_api_and_db_query_results(api_result=fetched_user, db_dict=to_json(user))


def test_read_non_existent_user_superuser(
    client: TestClient, superuser_token_headers: dict[str, str], db: Session
) -> None:
    user_id = generate_uuid()
    while crud.user.get(db, id=user_id):
        user_id = generate_uuid()
    r = client.get(f"{settings.API_V1_STR}/users/{user_id}", headers=superuser_token_headers)
    assert r.status_code == 404


def test_read_user_normal_admin(client: TestClient, admin_user_token_headers: dict[str, str], db: Session) -> None:
    user = create_random_user(db, type="student")
    r = client.get(f"{settings.API_V1_STR}/users/{user.id}", headers=admin_user_token_headers)
    assert r.status_code == 403


def test_read_user_normal_user(client: TestClient, normal_user_token_headers: dict[str, str], db: Session) -> None:
    user = create_random_user(db, type="student")
    r = client.get(f"{settings.API_V1_STR}/users/{user.id}", headers=normal_user_token_headers)
    assert r.status_code == 403


def test_update_user_superuser(client: TestClient, superuser_token_headers: dict[str, str], db: Session) -> None:
    user = create_random_user(db, type="student")
    full_name = random_lower_string()
    data = {"full_name": full_name}
    r = client.put(
        f"{settings.API_V1_STR}/users/{user.id}",
        headers=superuser_token_headers,
        json=data,
    )
    assert r.status_code == 200
    updated_user = r.json()
    db.refresh(user)
    compare_api_and_db_query_results(api_result=updated_user, db_dict=to_json(user))


def test_update_non_existent_user_superuser(
    client: TestClient, superuser_token_headers: dict[str, str], db: Session
) -> None:
    user_id = generate_uuid()
    while crud.user.get(db, id=user_id):
        user_id = generate_uuid()
    full_name = random_lower_string()
    data = {"full_name": full_name}
    r = client.put(
        f"{settings.API_V1_STR}/users/{user_id}",
        headers=superuser_token_headers,
        json=data,
    )
    assert r.status_code == 404


def test_update_user_normal_user(client: TestClient, normal_user_token_headers: dict[str, str], db: Session) -> None:
    user = create_random_user(db, type="student")
    full_name = random_lower_string()
    email = random_email()
    password = random_password()
    data = {"full_name": full_name, "email": email, "password": password}
    r = client.put(
        f"{settings.API_V1_STR}/users/{user.id}",
        headers=normal_user_token_headers,
        json=data,
    )
    assert r.status_code == 403


def test_update_nonpromotable_user(client: TestClient, superuser_token_headers: dict[str, str], db: Session) -> None:
    user = create_random_user(db, type="superuser")
    data = {"type": "admin"}
    r = client.put(
        f"{settings.API_V1_STR}/users/{user.id}",
        headers=superuser_token_headers,
        json=data,
    )
    assert r.status_code == 400


def test_update_nonpromoteable_role(client: TestClient, superuser_token_headers: dict[str, str], db: Session) -> None:
    user = create_random_user(db, type="professor")
    data = {"type": "superuser"}
    r = client.put(
        f"{settings.API_V1_STR}/users/{user.id}",
        headers=superuser_token_headers,
        json=data,
    )
    assert r.status_code == 400


def test_promote_professor(client: TestClient, superuser_token_headers: dict[str, str], db: Session) -> None:
    user = create_random_user(db, type="professor")
    data = {"is_admin": True}
    r = client.put(
        f"{settings.API_V1_STR}/users/{user.id}",
        headers=superuser_token_headers,
        json=data,
    )
    assert r.status_code == 200
    admin = crud.admin.get(db, id=user.id)
    assert admin
    assert admin.permissions == 0


def test_demote_admin(client: TestClient, superuser_token_headers: dict[str, str], db: Session) -> None:
    user = create_random_user(db, type="admin")
    data = {"is_admin": False}
    r = client.put(
        f"{settings.API_V1_STR}/users/{user.id}",
        headers=superuser_token_headers,
        json=data,
    )
    assert r.status_code == 400


def test_update_profile_picture_superuser(
    client: TestClient, superuser_token_headers: dict[str, str], db: Session
) -> None:
    user = create_random_user(db, type="student")
    response = client.get("https://media.rev-amp.tech/logo/revamp.png")
    with open("/tmp/profile_picture.png", "wb") as f:
        f.write(response.content)
    assert user.profile_picture is None
    r = client.put(
        f"{settings.API_V1_STR}/users/{user.id}/profile_picture",
        headers=superuser_token_headers,
        files={"image": ("profile_picture.png", open("/tmp/profile_picture.png", "rb").read(), "image/png")},
    )
    updated_user = r.json()
    db.refresh(user)
    assert r.status_code == 200
    compare_api_and_db_query_results(api_result=updated_user, db_dict=to_json(user))
    assert isfile(f"profile_pictures/{updated_user['profile_picture']}")
    remove(f"profile_pictures/{updated_user['profile_picture']}")


def test_update_profile_picture_superuser_non_existent_user(
    client: TestClient, superuser_token_headers: dict[str, str], db: Session
) -> None:
    user_id = generate_uuid()
    while crud.user.get(db, id=user_id):
        user_id = generate_uuid()
    response = client.get("https://media.rev-amp.tech/logo/revamp.png")
    with open("/tmp/profile_picture.png", "wb") as f:
        f.write(response.content)
    r = client.put(
        f"{settings.API_V1_STR}/users/{user_id}/profile_picture",
        headers=superuser_token_headers,
        files={"image": ("profile_picture.png", open("/tmp/profile_picture.png", "rb").read(), "image/png")},
    )
    assert r.status_code == 404


def test_update_profile_picture_superuser_not_image(
    client: TestClient, superuser_token_headers: dict[str, str], db: Session
) -> None:
    user = create_random_user(db, type="student")
    response = client.get("https://files.rev-amp.tech/README.md")
    with open("/tmp/README.md", "wb") as f:
        f.write(response.content)
    assert user.profile_picture is None
    r = client.put(
        f"{settings.API_V1_STR}/users/{user.id}/profile_picture",
        headers=superuser_token_headers,
        files={"image": ("README.md", open("/tmp/README.md", "rb").read(), "text/markdown")},
    )
    assert r.status_code == 415


def test_update_profile_picture_normal_user(
    client: TestClient, normal_user_token_headers: dict[str, str], db: Session
) -> None:
    user = create_random_user(db, type="student")
    response = client.get("https://media.rev-amp.tech/logo/revamp.png")
    with open("/tmp/profile_picture.png", "wb") as f:
        f.write(response.content)
    assert user.profile_picture is None
    r = client.put(
        f"{settings.API_V1_STR}/users/{user.id}/profile_picture",
        headers=normal_user_token_headers,
        files={"image": ("profile_picture.png", open("/tmp/profile_picture.png", "rb").read(), "image/png")},
    )
    assert r.status_code == 403


def test_update_profile_picture_normal_user_self(
    client: TestClient, superuser_token_headers: dict[str, str], db: Session
) -> None:
    user = create_random_user(db, type="student")
    response = client.get("https://media.rev-amp.tech/logo/revamp.png")
    with open("/tmp/profile_picture.png", "wb") as f:
        f.write(response.content)
    assert user.profile_picture is None
    r = client.put(
        f"{settings.API_V1_STR}/users/{user.id}/profile_picture",
        headers=authentication_token_from_email(client=client, email=user.email, db=db),
        files={"image": ("profile_picture.png", open("/tmp/profile_picture.png", "rb").read(), "image/png")},
    )
    updated_user = r.json()
    db.refresh(user)
    assert r.status_code == 200
    compare_api_and_db_query_results(api_result=updated_user, db_dict=to_json(user))
    assert isfile(f"profile_pictures/{updated_user['profile_picture']}")
    remove(f"profile_pictures/{updated_user['profile_picture']}")
