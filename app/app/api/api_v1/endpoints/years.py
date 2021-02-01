from typing import Any, List

from fastapi import APIRouter, Depends
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
