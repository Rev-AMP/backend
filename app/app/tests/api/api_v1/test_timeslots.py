from datetime import datetime, timedelta
from typing import Dict

from sqlalchemy.orm import Session
from starlette.testclient import TestClient

from app import crud
from app.core.config import settings
from app.schemas.users.admin import AdminPermissions
from app.tests.utils.timeslot import create_random_timeslot
from app.tests.utils.user import authentication_token_from_email, create_random_user
from app.tests.utils.utils import compare_api_and_db_query_results, to_json
from app.utils import generate_uuid


def test_get_all_timeslots(client: TestClient, superuser_token_headers: Dict[str, str], db: Session) -> None:
    timeslot = create_random_timeslot(db)
    r = client.get(f"{settings.API_V1_STR}/timeslots/", headers=superuser_token_headers)
    assert r.status_code == 200
    results = r.json()
    assert results
    compare_api_and_db_query_results(api_result=results[-1], db_dict=to_json(timeslot))


def test_get_timeslot_existing(client: TestClient, superuser_token_headers: Dict[str, str], db: Session) -> None:
    timeslot = create_random_timeslot(db)
    r = client.get(f"{settings.API_V1_STR}/timeslots/{timeslot.id}", headers=superuser_token_headers)
    assert r.status_code == 200
    fetched_timeslot = r.json()
    assert fetched_timeslot
    compare_api_and_db_query_results(api_result=fetched_timeslot, db_dict=to_json(timeslot))


def test_get_timeslot_nonexisting(client: TestClient, superuser_token_headers: Dict[str, str], db: Session) -> None:
    r = client.get(f"{settings.API_V1_STR}/timeslots/{generate_uuid()}", headers=superuser_token_headers)
    assert r.status_code == 404


def test_create_timeslot(client: TestClient, superuser_token_headers: Dict[str, str], db: Session) -> None:
    start_time = datetime.now().time()
    end_time = (datetime.now() + timedelta(hours=1)).time()
    data = {
        "start_time": start_time.isoformat(),
        "end_time": end_time.isoformat(),
    }
    r = client.post(f"{settings.API_V1_STR}/timeslots/", headers=superuser_token_headers, json=data)
    assert r.status_code == 200
    created_timeslot = r.json()
    fetched_timeslot = crud.timeslot.get_by_details(
        db,
        start_time=start_time,
        end_time=end_time,
    )
    assert fetched_timeslot
    compare_api_and_db_query_results(api_result=created_timeslot, db_dict=to_json(fetched_timeslot))
    compare_api_and_db_query_results(data, created_timeslot)


def test_create_timeslot_existing(client: TestClient, superuser_token_headers: Dict[str, str], db: Session) -> None:
    timeslot = create_random_timeslot(db)
    assert timeslot.start_time
    assert timeslot.end_time
    data = {
        "start_time": timeslot.start_time.isoformat(),
        "end_time": timeslot.end_time.isoformat(),
    }
    r = client.post(f"{settings.API_V1_STR}/timeslots/", headers=superuser_token_headers, json=data)
    assert r.status_code == 409


def test_update_timeslot(client: TestClient, superuser_token_headers: Dict[str, str], db: Session) -> None:
    timeslot = create_random_timeslot(db)
    start_time = datetime.now().time()
    end_time = (datetime.now() + timedelta(hours=1)).time()
    data = {
        "start_time": start_time.isoformat(),
        "end_time": end_time.isoformat(),
    }
    r = client.put(f"{settings.API_V1_STR}/timeslots/{timeslot.id}", headers=superuser_token_headers, json=data)
    fetched_timeslot = r.json()
    db.refresh(timeslot)
    assert fetched_timeslot
    compare_api_and_db_query_results(api_result=fetched_timeslot, db_dict=to_json(timeslot))


def test_update_timeslot_nonexisting(client: TestClient, superuser_token_headers: Dict[str, str], db: Session) -> None:
    r = client.put(f"{settings.API_V1_STR}/timeslots/{generate_uuid()}", headers=superuser_token_headers, json={})
    assert r.status_code == 404


def test_delete_timeslot(client: TestClient, superuser_token_headers: Dict[str, str], db: Session) -> None:
    timeslot = create_random_timeslot(db)
    r = client.delete(f"{settings.API_V1_STR}/timeslots/{timeslot.id}", headers=superuser_token_headers)
    assert r.status_code == 200
    deleted_timeslot = crud.timeslot.get(db, id=timeslot.id)
    assert deleted_timeslot is None


def test_delete_timeslot_nonexisting(client: TestClient, superuser_token_headers: Dict[str, str], db: Session) -> None:
    r = client.delete(f"{settings.API_V1_STR}/timeslots/{generate_uuid()}", headers=superuser_token_headers)
    assert r.status_code == 404


def test_get_timeslot_normal_user(client: TestClient, normal_user_token_headers: Dict[str, str], db: Session) -> None:
    r = client.get(f"{settings.API_V1_STR}/timeslots/", headers=normal_user_token_headers)
    assert r.status_code == 403


def test_get_timeslot_admin(client: TestClient, db: Session) -> None:
    admin_perms = AdminPermissions(0)
    admin_perms["timeslot"] = True
    admin = create_random_user(db=db, type="admin", permissions=admin_perms.permissions)
    admin_user_token_headers = authentication_token_from_email(
        client=client, db=db, email=admin.email, user_type="admin"
    )
    r = client.get(f"{settings.API_V1_STR}/timeslots/", headers=admin_user_token_headers)
    assert r.status_code == 200


def test_get_timeslot_weakadmin(client: TestClient, db: Session) -> None:
    admin = create_random_user(db=db, type="admin", permissions=0)
    admin_user_token_headers = authentication_token_from_email(
        client=client, db=db, email=admin.email, user_type="admin"
    )
    r = client.get(f"{settings.API_V1_STR}/timeslots/", headers=admin_user_token_headers)
    assert r.status_code == 403
