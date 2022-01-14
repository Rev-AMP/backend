import logging
from typing import Any

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app import crud, models, schemas
from app.api import deps
from app.exceptions import ConflictException, NotFoundException

router = APIRouter()


@router.get("/", response_model=list[schemas.Lecture])
def read_lectures(
    db: Session = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100,
    _: models.Admin = Depends(deps.get_current_admin_with_permission("school")),
) -> Any:
    return crud.lecture.get_multi(db, skip=skip, limit=limit)


@router.get("/{lecture_id}", response_model=schemas.Lecture)
def read_lecture_by_id(
    *,
    db: Session = Depends(deps.get_db),
    lecture_id: str,
    _: models.Admin = Depends(deps.get_current_admin_with_permission("school")),
) -> Any:
    if lecture := crud.lecture.get(db, id=lecture_id):
        return lecture
    raise NotFoundException(detail="A lecture with this ID does not exist!")


@router.get("/division/{division_id}", response_model=list[schemas.Lecture])
def get_lectures_for_division(
    *, db: Session = Depends(deps.get_db), division_id: str, _: models.User = Depends(deps.get_current_user)
) -> Any:
    if crud.division.get(db, id=division_id):
        return crud.lecture.get_by_division(db, division_id=division_id)
    raise NotFoundException(detail="A division with this ID does not exist!")


@router.post("/", response_model=schemas.Lecture)
def create_lecture(
    *,
    db: Session = Depends(deps.get_db),
    lecture_in: schemas.LectureCreate,
    current_admin: models.Admin = Depends(deps.get_current_admin_with_permission("school")),
) -> Any:

    if crud.lecture.get_by_details(
        db,
        day=lecture_in.day,
        time_slot_id=lecture_in.time_slot_id,
        division_id=lecture_in.division_id,
        type=lecture_in.type,
        room_number=lecture_in.room_number,
    ):
        raise ConflictException(
            detail="A lecture with these details already exists in the system!",
        )

    logging.info(
        f"Admin {current_admin.user_id} ({current_admin.user.email}) is creating lecture {lecture_in.__dict__}"
    )
    return crud.lecture.create(db, obj_in=lecture_in)


@router.put("/{lecture_id}", response_model=schemas.Lecture)
def update_lecture(
    *,
    db: Session = Depends(deps.get_db),
    lecture_id: str,
    lecture_in: schemas.LectureUpdate,
    current_admin: models.Admin = Depends(deps.get_current_admin_with_permission("school")),
) -> Any:
    if lecture := crud.lecture.get(db, id=lecture_id):
        logging.info(f"Admin {current_admin.user_id} ({current_admin.user.email}) is updating lecture {lecture.id}")
        return crud.lecture.update(db, db_obj=lecture, obj_in=lecture_in)
    raise NotFoundException(detail="The lecture with this ID does not exist in the system!")


@router.delete("/{lecture_id}")
def delete_lecture(
    *,
    db: Session = Depends(deps.get_db),
    lecture_id: str,
    current_admin: models.Admin = Depends(deps.get_current_admin_with_permission("school")),
) -> Any:
    if lecture := crud.lecture.get(db, id=lecture_id):
        logging.info(f"Admin {current_admin.user_id} ({current_admin.user.email}) is deleting lecture {lecture.id}")
        return crud.lecture.remove(db, id=lecture_id)
    raise NotFoundException(detail="The lecture with this ID does not exist in the system!")
