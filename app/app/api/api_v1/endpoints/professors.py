import logging
from typing import Any, List

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app import crud, models, schemas
from app.api import deps
from app.exceptions import ForbiddenException, NotFoundException
from app.schemas import AdminPermissions

router = APIRouter()


@router.get("/", response_model=List[schemas.Professor])
def read_professors(
    db: Session = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100,
    _: models.Admin = Depends(deps.get_current_active_admin_with_permission("professor")),
) -> Any:
    """
    Retrieve professors
    """
    return crud.professor.get_multi(db, skip=skip, limit=limit)


@router.get("/me", response_model=schemas.Professor)
def get_professor_me(
    current_professor: models.Professor = Depends(deps.get_current_professor),
) -> Any:
    """
    Get current professor
    """
    return current_professor


@router.get("/me/divisions", response_model=List[schemas.Division])
def get_professor_divisions(
    current_professor: models.Professor = Depends(deps.get_current_professor),
    db: Session = Depends(deps.get_db),
) -> Any:
    """
    Get all divisions for current professor
    """
    return crud.division.get_all_divisions_for_professor(db, professor_id=current_professor.user_id)


@router.get("/{professor_id}", response_model=schemas.Professor)
def read_professor_by_id(
    professor_id: int, current_user: models.User = Depends(deps.get_current_user), db: Session = Depends(deps.get_db)
) -> Any:
    """
    Get a specific professor by ID.
    """

    # Fetch professor with the corresponding ID from DB
    professor = crud.professor.get(db, id=professor_id)

    # Return the fetched object without checking perms if current_professor is trying to fetch itself
    if current_user.id == professor_id:
        return professor

    # check perms and return if professor exists, else 404
    if (admin := crud.admin.get(db, id=current_user.id)) and AdminPermissions(admin.permissions).is_allowed(
        "professor"
    ):
        if professor:
            return professor
        raise NotFoundException(
            detail="The professor with this ID does not exist in the system",
        )

    raise ForbiddenException(detail="The user doesn't have enough privileges")


@router.get("/{professor_id}/divisions", response_model=List[schemas.Division])
def read_professor_divisions_by_id(
    professor_id: int, current_user: models.User = Depends(deps.get_current_user), db: Session = Depends(deps.get_db)
) -> Any:
    """
    Get all divisions for a specific professor by ID.
    """

    # Fetch professor with the corresponding ID from DB
    professor = crud.professor.get(db, id=professor_id)

    # Return the fetched object without checking perms if current_professor is trying to fetch itself
    if professor and current_user.id == professor_id:
        return crud.division.get_all_divisions_for_professor(db, professor_id=professor.user_id)

    # check perms and return if professor exists, else 404
    if (admin := crud.admin.get(db, id=current_user.id)) and AdminPermissions(admin.permissions).is_allowed(
        "professor"
    ):
        if professor:
            return crud.division.get_all_divisions_for_professor(db, professor_id=professor.user_id)
        raise NotFoundException(
            detail="The professor with this ID does not exist in the system",
        )

    raise ForbiddenException(detail="The user doesn't have enough privileges")


@router.put("/{professor_id}", response_model=schemas.Professor)
def update_professor(
    *,
    db: Session = Depends(deps.get_db),
    professor_id: int,
    professor_in: schemas.ProfessorUpdate,
    current_admin: models.Admin = Depends(deps.get_current_active_admin_with_permission("professor")),
) -> Any:
    """
    Update professor.
    """

    if professor := crud.professor.get(db, id=professor_id):
        logging.info(
            f"Admin {current_admin.user_id} ({current_admin.user.email}) is updating professor {professor.user_id}"
            f"({professor.user.email}) to {professor_in.__dict__}"
        )
        return crud.professor.update(db, db_obj=professor, obj_in=professor_in)

    raise NotFoundException(
        detail="This professor does not exist!",
    )
