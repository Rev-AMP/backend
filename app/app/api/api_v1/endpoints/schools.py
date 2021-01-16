from typing import Any, List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app import crud, models, schemas
from app.api import deps

router = APIRouter()


@router.get("/", response_model=List[schemas.School])
def read_schools(
    db: Session = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100,
    current_user: models.User = Depends(deps.get_current_active_superuser),
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
    current_user: models.User = Depends(deps.get_current_active_superuser),
) -> Any:
    """
    Create new school.
    """
    # Check if the school already exists; raise HTTPException with error code 400 if it does
    school = crud.school.get_by_name(db, name=school_in.name)
    if school:
        raise HTTPException(
            status_code=400,
            detail="The user with this name already exists in the system.",
        )

    # Create new school
    school = crud.school.create(db, obj_in=school_in)

    return school


@router.get("/{school_id}", response_model=schemas.School)
def read_school_by_id(
    school_id: int,
    current_user: models.User = Depends(deps.get_current_active_user),
    db: Session = Depends(deps.get_db),
) -> Any:
    """
    Get a specific school by id.
    """

    # Fetch School with the corresponding id from db
    school = crud.school.get(db, id=school_id)

    # TODO: check the perms of admin, or if user belongs to the school
    # Raise exception if fetched School is not the current_user and the current_user is not a superuser
    if (
        not crud.user.is_superuser(current_user)
        and not crud.user.check_admin(current_user)
        and not current_user.school == school_id
    ):
        raise HTTPException(status_code=400, detail="The user doesn't have enough privileges")

    return school


@router.put("/{school_id}", response_model=schemas.School)
def update_school(
    *,
    db: Session = Depends(deps.get_db),
    school_id: int,
    school_in: schemas.SchoolUpdate,
    current_user: models.User = Depends(deps.get_current_active_superuser),
) -> Any:
    """
    Update a school.
    """

    # Fetch existing school object from db
    school = crud.school.get(db, id=school_id)
    if not school:
        raise HTTPException(
            status_code=400,
            detail="The school with this ID does not exist in the system",
        )

    # Save updated object based on given SchoolUpdate object in db
    school = crud.school.update(db, db_obj=school, obj_in=school_in)

    return school


@router.get("/{school_id}/students", response_model=List[schemas.User])
def get_students(
    *,
    db: Session = Depends(deps.get_db),
    school_id: int,
    current_user: models.User = Depends(deps.get_current_active_superuser),
) -> Any:
    """
    Get all students belonging to a school.
    """
    return crud.school.get_all_students(db, school_id=school_id)


@router.get("/{school_id}/professors", response_model=List[schemas.User])
def get_professors(
    *,
    db: Session = Depends(deps.get_db),
    school_id: int,
    current_user: models.User = Depends(deps.get_current_active_superuser),
) -> Any:
    """
    Get all students belonging to a school.
    """
    return crud.school.get_all_professors(db, school_id=school_id)
