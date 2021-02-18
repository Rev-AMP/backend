from typing import Any, List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app import crud, models, schemas
from app.api import deps

router = APIRouter()


@router.get("/", response_model=List[schemas.Year])
def read_years(
    db: Session = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100,
    current_admin: models.Admin = Depends(deps.get_current_active_admin_with_permission("year")),
) -> Any:
    """
    Retrieve years
    """
    return crud.year.get_multi(db, skip=skip, limit=limit)


@router.get("/{year_id}", response_model=schemas.Year)
def read_year_by_id(
    *,
    db: Session = Depends(deps.get_db),
    year_id: int,
    current_admin: models.Admin = Depends(deps.get_current_active_admin_with_permission("year")),
) -> Any:
    """
    Retrieve years
    """
    if year := crud.year.get(db, year_id):
        return year
    raise HTTPException(status_code=404, detail="The year with this ID does not exist!")


@router.post("/", response_model=schemas.Year)
def create_year(
    *,
    db: Session = Depends(deps.get_db),
    year_in: schemas.YearCreate,
    current_admin: models.Admin = Depends(deps.get_current_active_admin_with_permission("year")),
) -> Any:

    if crud.year.get_by_details(
        db, school_id=year_in.school_id, start_year=year_in.start_year, end_year=year_in.end_year
    ):
        raise HTTPException(
            status_code=409,
            detail="The year with these details already exists in the system!",
        )

    return crud.year.create(db, obj_in=year_in)


@router.put("/{year_id}", response_model=schemas.Year)
def update_year(
    *,
    db: Session = Depends(deps.get_db),
    year_id: int,
    year_in: schemas.YearUpdate,
    current_admin: models.Admin = Depends(deps.get_current_active_admin_with_permission("year")),
) -> Any:
    if year := crud.year.get(db, year_id):
        return crud.year.update(db, db_obj=year, obj_in=year_in)
    raise HTTPException(status_code=404, detail="The year with this ID does not exist in the system!")


@router.delete("/{year_id}")
def delete_year(
    *,
    db: Session = Depends(deps.get_db),
    year_id: int,
    current_admin: models.Admin = Depends(deps.get_current_active_admin_with_permission("year")),
) -> Any:
    if crud.year.get(db, year_id):
        return crud.year.remove(db, id=year_id)
    raise HTTPException(status_code=404, detail="The year with this ID does not exist in the system!")
