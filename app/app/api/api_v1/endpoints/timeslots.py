import logging
from typing import Any, List

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app import crud, models, schemas
from app.api import deps
from app.exceptions import ConflictException, NotFoundException

router = APIRouter()


@router.get("/", response_model=List[schemas.TimeSlot])
def read_timeslots(
    db: Session = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100,
    _: models.Admin = Depends(deps.get_current_admin_with_permission("school")),
) -> Any:
    return crud.timeslot.get_multi(db, skip=skip, limit=limit)


@router.get("/{timeslot_id}", response_model=schemas.TimeSlot)
def read_timeslot_by_id(
    *,
    db: Session = Depends(deps.get_db),
    timeslot_id: str,
    _: models.Admin = Depends(deps.get_current_admin_with_permission("school")),
) -> Any:
    if timeslot := crud.timeslot.get(db, id=timeslot_id):
        return timeslot
    raise NotFoundException(detail="The timeslot with this ID does not exist!")


@router.post("/", response_model=schemas.TimeSlot)
def create_timeslot(
    *,
    db: Session = Depends(deps.get_db),
    timeslot_in: schemas.TimeSlotCreate,
    current_admin: models.Admin = Depends(deps.get_current_admin_with_permission("school")),
) -> Any:

    if crud.timeslot.get_by_details(
        db,
        start_time=timeslot_in.start_time,
        end_time=timeslot_in.end_time,
    ):
        raise ConflictException(
            detail="The timeslot with these details already exists in the system!",
        )

    logging.info(
        f"Admin {current_admin.user_id} ({current_admin.user.email}) is creating timeslot {timeslot_in.__dict__}"
    )
    return crud.timeslot.create(db, obj_in=timeslot_in)


@router.put("/{timeslot_id}", response_model=schemas.TimeSlot)
def update_timeslot(
    *,
    db: Session = Depends(deps.get_db),
    timeslot_id: str,
    timeslot_in: schemas.TimeSlotUpdate,
    current_admin: models.Admin = Depends(deps.get_current_admin_with_permission("school")),
) -> Any:
    if timeslot := crud.timeslot.get(db, id=timeslot_id):
        logging.info(
            f"Admin {current_admin.user_id} ({current_admin.user.email}) is updating timeslot {timeslot.id} (start - "
            f"{timeslot.start_time}, end - {timeslot.end_time}) to {timeslot_in.__dict__}"
        )
        return crud.timeslot.update(db, db_obj=timeslot, obj_in=timeslot_in)
    raise NotFoundException(detail="The timeslot with this ID does not exist in the system!")


@router.delete("/{timeslot_id}")
def delete_timeslot(
    *,
    db: Session = Depends(deps.get_db),
    timeslot_id: str,
    current_admin: models.Admin = Depends(deps.get_current_admin_with_permission("school")),
) -> Any:
    if timeslot := crud.timeslot.get(db, id=timeslot_id):
        logging.info(
            f"Admin {current_admin.user_id} ({current_admin.user.email}) is deleting timeslot {timeslot.id} (start - "
            f"{timeslot.start_time}, end - {timeslot.end_time})"
        )
        return crud.timeslot.remove(db, id=timeslot_id)
    raise NotFoundException(detail="The timeslot with this ID does not exist in the system!")
