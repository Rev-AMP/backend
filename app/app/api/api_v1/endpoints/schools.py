import logging
from typing import Any

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app import crud, models, schemas
from app.api import deps
from app.exceptions import ConflictException, ForbiddenException, NotFoundException

router = APIRouter()


@router.get("/", response_model=list[schemas.School])
def read_schools(
    db: Session = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100,
    _: models.Admin = Depends(deps.get_current_admin_with_permission("school")),
) -> Any:
    """
    Retrieve schools.
    """
    schools = crud.school.get_multi(db, skip=skip, limit=limit)
    return schools


@router.post("/", response_model=schemas.School)
def create_school(
    *,
    db: Session = Depends(deps.get_db),
    school_in: schemas.SchoolCreate,
    current_admin: models.Admin = Depends(deps.get_current_admin_with_permission("school")),
) -> Any:
    """
    Create new school.
    """
    # Check if the school already exists; raise Exception with error code 409 if it does
    if crud.school.get_by_name(db, name=school_in.name):
        raise ConflictException(
            detail="A school with this name already exists in the system.",
        )

    # Check if a school with this head already exists; raise Exception with error code 409 if it does
    if crud.school.get_by_head(db, head=school_in.head):
        raise ConflictException(
            detail="A school with this head already exists in the system.",
        )

    # Create new school
    logging.info(f"Admin {current_admin.user_id} ({current_admin.user.email}) is creating School {school_in.__dict__}")
    school = crud.school.create(db, obj_in=school_in)

    return school


@router.get("/{school_id}", response_model=schemas.School)
def read_school_by_id(
    school_id: str,
    current_user: models.User = Depends(deps.get_current_user),
    db: Session = Depends(deps.get_db),
) -> Any:
    """
    Get a specific school by id.
    """

    # Fetch School with the corresponding id from db
    school = crud.school.get(db, id=school_id)

    # Raise exception if the current_user doesn't belong to the fetched School and the current_user doesn't have perms
    if current_user.school_id == school_id:
        return school

    if current_user.is_admin:
        if admin := crud.admin.get(db, current_user.id):
            if schemas.AdminPermissions(admin.permissions).is_allowed("school"):
                if school:
                    return school
                raise NotFoundException(
                    detail="The school with this ID does not exist in the system",
                )

    raise ForbiddenException(detail="The user doesn't have enough privileges")


@router.put("/{school_id}", response_model=schemas.School)
def update_school(
    *,
    db: Session = Depends(deps.get_db),
    school_id: str,
    school_in: schemas.SchoolUpdate,
    current_admin: models.Admin = Depends(deps.get_current_admin_with_permission("school")),
) -> Any:
    """
    Update a school.
    """

    # Fetch existing school object from db
    school = crud.school.get(db, id=school_id)
    if not school:
        raise NotFoundException(
            detail="The school with this ID does not exist in the system",
        )

    logging.info(
        f"Admin {current_admin.user_id} ({current_admin.user.email}) is updating School {school.id} "
        f"({school.name}) to {school_in.__dict__}"
    )

    # Save updated object based on given SchoolUpdate object in db
    return crud.school.update(db, db_obj=school, obj_in=school_in)


@router.get("/{school_id}/students", response_model=list[schemas.User])
def get_students(
    *,
    db: Session = Depends(deps.get_db),
    school_id: str,
    _: models.Admin = Depends(deps.get_current_admin_with_permission("school")),
) -> Any:
    """
    Get all students belonging to a school.
    """
    return crud.user.get_all_students_for_school(db, school_id=school_id)


@router.get("/{school_id}/professors", response_model=list[schemas.User])
def get_professors(
    *,
    db: Session = Depends(deps.get_db),
    school_id: str,
    _: models.Admin = Depends(deps.get_current_admin_with_permission("school")),
) -> Any:
    """
    Get all students belonging to a school.
    """
    return crud.user.get_all_professors_for_school(db, school_id=school_id)


@router.get("/{school_id}/timeslots", response_model=list[schemas.TimeSlot])
def get_timeslots(
    *,
    db: Session = Depends(deps.get_db),
    school_id: str,
    _: models.Admin = Depends(deps.get_current_admin_with_permission("school")),
) -> Any:
    """
    Get all timeslots in a school
    """
    return crud.timeslot.get_by_school(db, school_id=school_id)


@router.delete("/{school_id}")
def delete_school(
    *,
    db: Session = Depends(deps.get_db),
    school_id: str,
    current_admin: models.Admin = Depends(deps.get_current_admin_with_permission("school")),
) -> Any:
    if school := crud.school.get(db, school_id):
        logging.info(
            f"Admin {current_admin.user_id} ({current_admin.user.email}) is deleting School {school.id} ({school.name})"
        )
        return crud.school.remove(db, id=school_id)
    raise NotFoundException(detail="The school with this ID does not exist in the system!")
