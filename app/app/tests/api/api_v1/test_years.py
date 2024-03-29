from datetime import datetime

from sqlalchemy.orm import Session
from starlette.testclient import TestClient

from app import crud
from app.core.config import settings
from app.schemas.users.admin import AdminPermissions
from app.tests.utils.user import authentication_token_from_email, create_random_user
from app.tests.utils.utils import (
    compare_api_and_db_query_results,
    random_lower_string,
    to_json,
)
from app.tests.utils.year import create_random_school, create_random_year
from app.utils import generate_uuid


def test_get_all_years(client: TestClient, superuser_token_headers: dict[str, str], db: Session) -> None:
    create_random_year(db)
    r = client.get(f"{settings.API_V1_STR}/years/", headers=superuser_token_headers)
    assert r.status_code == 200
    results = r.json()
    assert results


def test_get_year_existing(client: TestClient, superuser_token_headers: dict[str, str], db: Session) -> None:
    year = create_random_year(db)
    r = client.get(f"{settings.API_V1_STR}/years/{year.id}", headers=superuser_token_headers)
    assert r.status_code == 200
    fetched_year = r.json()
    assert fetched_year
    compare_api_and_db_query_results(api_result=fetched_year, db_dict=to_json(year))


def test_get_year_nonexisting(client: TestClient, superuser_token_headers: dict[str, str], db: Session) -> None:
    r = client.get(f"{settings.API_V1_STR}/years/{generate_uuid()}", headers=superuser_token_headers)
    assert r.status_code == 404


def test_create_year(client: TestClient, superuser_token_headers: dict[str, str], db: Session) -> None:
    school_id = create_random_school(db).id
    start_year = datetime.now().year
    end_year = start_year + 1
    name = random_lower_string()
    data = {
        "name": name,
        "school_id": school_id,
        "start_year": start_year,
        "end_year": end_year,
    }
    r = client.post(f"{settings.API_V1_STR}/years/", headers=superuser_token_headers, json=data)
    assert r.status_code == 200
    created_year = r.json()
    year = crud.year.get_by_details(db, name=name, school_id=school_id, start_year=start_year, end_year=end_year)
    assert year
    compare_api_and_db_query_results(api_result=created_year, db_dict=to_json(year))
    compare_api_and_db_query_results(data, created_year)


def test_create_year_existing(client: TestClient, superuser_token_headers: dict[str, str], db: Session) -> None:
    year = create_random_year(db)
    data = {
        "name": year.name,
        "school_id": year.school_id,
        "start_year": year.start_year,
        "end_year": year.end_year,
    }
    r = client.post(f"{settings.API_V1_STR}/years/", headers=superuser_token_headers, json=data)
    assert r.status_code == 409


def test_get_year_normal_user(client: TestClient, normal_user_token_headers: dict[str, str], db: Session) -> None:
    r = client.get(f"{settings.API_V1_STR}/years/", headers=normal_user_token_headers)
    assert r.status_code == 403


def test_update_year_nonexisting(client: TestClient, superuser_token_headers: dict[str, str], db: Session) -> None:
    r = client.put(f"{settings.API_V1_STR}/years/{generate_uuid()}", headers=superuser_token_headers, json={})
    assert r.status_code == 404


def test_update_year(client: TestClient, superuser_token_headers: dict[str, str], db: Session) -> None:
    year = create_random_year(db)
    assert year.start_year
    assert year.end_year
    data = {"start_year": year.start_year - 1, "end_year": year.end_year - 1, "is_active": not year.is_active}
    r = client.put(f"{settings.API_V1_STR}/years/{year.id}", headers=superuser_token_headers, json=data)
    assert r.status_code == 200
    fetched_year = r.json()
    db.refresh(year)
    assert fetched_year
    compare_api_and_db_query_results(api_result=fetched_year, db_dict=to_json(year))


def test_get_year_admin(client: TestClient, db: Session) -> None:
    admin_perms = AdminPermissions(0)
    admin_perms["year"] = True
    admin = create_random_user(db, "admin", permissions=admin_perms.permissions)
    admin_user_token_headers = authentication_token_from_email(
        client=client, db=db, email=admin.email, user_type="admin"
    )
    r = client.get(f"{settings.API_V1_STR}/years/", headers=admin_user_token_headers)
    assert r.status_code == 200


def test_get_year_weakadmin(client: TestClient, db: Session) -> None:
    admin = create_random_user(db, "admin", permissions=0)
    admin_user_token_headers = authentication_token_from_email(
        client=client, db=db, email=admin.email, user_type="admin"
    )
    r = client.get(f"{settings.API_V1_STR}/years/", headers=admin_user_token_headers)
    assert r.status_code == 403


def test_delete_year(client: TestClient, superuser_token_headers: dict[str, str], db: Session) -> None:
    year = create_random_year(db)
    r = client.delete(f"{settings.API_V1_STR}/years/{year.id}", headers=superuser_token_headers)
    assert r.status_code == 200
    deleted_year = crud.year.get(db, year.id)
    assert deleted_year is None


def test_delete_year_nonexisting(client: TestClient, superuser_token_headers: dict[str, str], db: Session) -> None:
    r = client.delete(f"{settings.API_V1_STR}/years/{generate_uuid()}", headers=superuser_token_headers)
    assert r.status_code == 404
