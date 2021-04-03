import logging
from typing import Any, List

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app import crud, models, schemas
from app.api import deps
from app.exceptions import ConflictException, NotFoundException

router = APIRouter()


@router.get("/", response_model=List[schemas.Year])
def read_years(
    db: Session = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100,
    _: models.Admin = Depends(deps.get_current_admin_with_permission("year")),
) -> Any:
    """
    Retrieve years
    """
    years = crud.year.get_multi(db, skip=skip, limit=limit)
    return years


@router.get("/{year_id}", response_model=schemas.Year)
def read_year_by_id(
    *,
    db: Session = Depends(deps.get_db),
    year_id: int,
    _: models.Admin = Depends(deps.get_current_admin_with_permission("year")),
) -> Any:
    """
    Retrieve years
    """
    if year := crud.year.get(db, year_id):
        return year
    raise NotFoundException(detail="The year with this ID does not exist!")


@router.post("/", response_model=schemas.Year)
def create_year(
    *,
    db: Session = Depends(deps.get_db),
    year_in: schemas.YearCreate,
    current_admin: models.Admin = Depends(deps.get_current_admin_with_permission("year")),
) -> Any:

    if crud.year.get_by_details(
        db, name=year_in.name, school_id=year_in.school_id, start_year=year_in.start_year, end_year=year_in.end_year
    ):
        raise ConflictException(
            detail="The year with these details already exists in the system!",
        )
    logging.info(f"Admin {current_admin.user_id} ({current_admin.user.email}) is creating Year {year_in.__dict__}")
    return crud.year.create(db, obj_in=year_in)


@router.put("/{year_id}", response_model=schemas.Year)
def update_year(
    *,
    db: Session = Depends(deps.get_db),
    year_id: int,
    year_in: schemas.YearUpdate,
    current_admin: models.Admin = Depends(deps.get_current_admin_with_permission("year")),
) -> Any:
    if year := crud.year.get(db, year_id):
        logging.info(
            f"Admin {current_admin.user_id} ({current_admin.user.email}) is updating Year {year.id} ({year.name}) to"
            f"{year_in.__dict__}"
        )
        return crud.year.update(db, db_obj=year, obj_in=year_in)
    raise NotFoundException(detail="The year with this ID does not exist in the system!")


@router.delete("/{year_id}")
def delete_year(
    *,
    db: Session = Depends(deps.get_db),
    year_id: int,
    current_admin: models.Admin = Depends(deps.get_current_admin_with_permission("year")),
) -> Any:
    if year := crud.year.get(db, year_id):
        logging.info(
            f"Admin {current_admin.user_id} ({current_admin.user.email}) is deleting Year {year.id} ({year.name})"
        )
        return crud.year.remove(db, id=year_id)
    raise NotFoundException(detail="The year with this ID does not exist in the system!")
