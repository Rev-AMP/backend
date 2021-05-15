from typing import Dict

from sqlalchemy.orm import Session
from starlette.testclient import TestClient

from app import crud
from app.core.config import settings
from app.schemas import AdminPermissions
from app.tests.utils.lecture import (
    create_random_lecture,
    get_random_day,
    get_random_lecture_type,
    get_random_room_number,
)
from app.tests.utils.user import authentication_token_from_email, create_random_user
from app.tests.utils.utils import (
    compare_api_and_db_query_results,
    random_email,
    to_json,
)
from app.utils import generate_uuid

from ...utils.division import create_random_division
from ...utils.timeslot import create_random_timeslot


def test_get_all_lectures(client: TestClient, superuser_token_headers: Dict[str, str], db: Session) -> None:
    lecture = create_random_lecture(db)
    r = client.get(f"{settings.API_V1_STR}/lectures/", headers=superuser_token_headers)
    assert r.status_code == 200
    results = r.json()
    assert results
    compare_api_and_db_query_results(api_result=results[-1], db_dict=to_json(lecture))


def test_create_lecture(client: TestClient, superuser_token_headers: Dict[str, str], db: Session) -> None:
    day = get_random_day()
    time_slot_id = create_random_timeslot(db).id
    division_id = create_random_division(db).id
    type_ = get_random_lecture_type()
    room_number = get_random_room_number()
    while crud.lecture.get_by_details(
        db=db, day=day, time_slot_id=time_slot_id, division_id=division_id, type=type_, room_number=room_number
    ):
        room_number = get_random_room_number()
    data = {
        "day": day,
        "time_slot_id": time_slot_id,
        "division_id": division_id,
        "type": type_,
        "room_number": room_number,
    }
    r = client.post(f"{settings.API_V1_STR}/lectures/", headers=superuser_token_headers, json=data)
    assert r.status_code == 200
    created_lecture = r.json()
    lecture = crud.lecture.get_by_details(
        db=db, day=day, time_slot_id=time_slot_id, division_id=division_id, type=type_, room_number=room_number
    )
    assert lecture
    compare_api_and_db_query_results(api_result=created_lecture, db_dict=to_json(lecture))


def test_create_lecture_existing(client: TestClient, superuser_token_headers: Dict[str, str], db: Session) -> None:
    lecture = create_random_lecture(db)
    data = {
        "day": lecture.day,
        "time_slot_id": lecture.time_slot_id,
        "division_id": lecture.division_id,
        "type": lecture.type,
        "room_number": lecture.room_number,
    }
    r = client.post(f"{settings.API_V1_STR}/lectures/", headers=superuser_token_headers, json=data)
    assert r.status_code == 409


def test_get_lecture_superuser(client: TestClient, superuser_token_headers: Dict[str, str], db: Session) -> None:
    lecture = create_random_lecture(db)
    r = client.get(f"{settings.API_V1_STR}/lectures/{lecture.id}", headers=superuser_token_headers)
    assert r.status_code == 200
    fetched_lecture = r.json()
    assert fetched_lecture
    compare_api_and_db_query_results(api_result=fetched_lecture, db_dict=to_json(lecture))


def test_get_non_existing_lecture_superuser(
    client: TestClient, superuser_token_headers: Dict[str, str], db: Session
) -> None:
    lecture_id = generate_uuid()
    r = client.get(f"{settings.API_V1_STR}/lectures/{lecture_id}", headers=superuser_token_headers)
    assert r.status_code == 404


def test_get_lecture_admin(client: TestClient, db: Session) -> None:
    lecture = create_random_lecture(db)
    perms = AdminPermissions(0)
    perms["school"] = True
    admin = create_random_user(db, "admin", permissions=perms.permissions)
    admin_user_token_headers = authentication_token_from_email(
        client=client, db=db, email=admin.email, user_type="admin"
    )
    r = client.get(f"{settings.API_V1_STR}/lectures/{lecture.id}", headers=admin_user_token_headers)
    assert r.status_code == 200
    fetched_lecture = r.json()
    assert fetched_lecture
    compare_api_and_db_query_results(api_result=fetched_lecture, db_dict=to_json(lecture))


def test_get_lecture_division_student(client: TestClient, db: Session) -> None:
    lecture = create_random_lecture(db)
    normal_user_token_headers = authentication_token_from_email(
        client=client,
        db=db,
        email=random_email(),
    )
    r = client.get(f"{settings.API_V1_STR}/lectures/division/{lecture.division_id}", headers=normal_user_token_headers)
    assert r.status_code == 200
    fetched_lecture = r.json()
    assert fetched_lecture
    assert len(fetched_lecture) > 0
    compare_api_and_db_query_results(api_result=fetched_lecture[0], db_dict=to_json(lecture))


def test_update_lecture(client: TestClient, superuser_token_headers: Dict[str, str], db: Session) -> None:
    lecture = create_random_lecture(db)
    new_timeslot = create_random_timeslot(db)
    data = {"time_slot_id": new_timeslot.id}
    r = client.put(f"{settings.API_V1_STR}/lectures/{lecture.id}", headers=superuser_token_headers, json=data)
    assert r.status_code == 200
    fetched_lecture = r.json()
    db.refresh(lecture)
    assert fetched_lecture
    compare_api_and_db_query_results(api_result=fetched_lecture, db_dict=to_json(lecture))


def test_update_lecture_nonexisting(client: TestClient, superuser_token_headers: Dict[str, str], db: Session) -> None:
    day = get_random_day()
    time_slot_id = create_random_timeslot(db).id
    division_id = create_random_division(db).id
    type_ = get_random_lecture_type()
    room_number = get_random_room_number()
    while crud.lecture.get_by_details(
        db=db, day=day, time_slot_id=time_slot_id, division_id=division_id, type=type_, room_number=room_number
    ):
        room_number = get_random_room_number()
    data = {
        "day": day,
        "time_slot_id": time_slot_id,
        "division_id": division_id,
        "type": type_,
        "room_number": room_number,
    }
    r = client.put(f"{settings.API_V1_STR}/lectures/{generate_uuid()}", headers=superuser_token_headers, json=data)
    assert r.status_code == 404


def test_delete_lecture(client: TestClient, superuser_token_headers: Dict[str, str], db: Session) -> None:
    lecture = create_random_lecture(db)
    r = client.delete(f"{settings.API_V1_STR}/lectures/{lecture.id}", headers=superuser_token_headers)
    assert r.status_code == 200
    deleted_lecture = crud.lecture.get(db, lecture.id)
    assert deleted_lecture is None


def test_delete_lecture_nonexisting(client: TestClient, superuser_token_headers: Dict[str, str], db: Session) -> None:
    r = client.delete(f"{settings.API_V1_STR}/lectures/{generate_uuid()}", headers=superuser_token_headers)
    assert r.status_code == 404
