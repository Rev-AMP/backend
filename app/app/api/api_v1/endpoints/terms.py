from typing import Any, List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app import crud, models, schemas
from app.api import deps

router = APIRouter()


@router.get("/", response_model=List[schemas.Term])
def read_terms(
    db: Session = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100,
    current_admin: models.Admin = Depends(deps.get_current_active_admin_with_permission("term")),
) -> Any:
    return crud.term.get_multi(db, skip=skip, limit=limit)


@router.get("/{term_id}", response_model=schemas.Term)
def read_term_by_id(
    *,
    db: Session = Depends(deps.get_db),
    term_id: int,
    current_admin: models.Admin = Depends(deps.get_current_active_admin_with_permission("term")),
) -> Any:
    if term := crud.term.get(db, term_id):
        return term
    raise HTTPException(status_code=404, detail="The term with this ID does not exist!")


@router.post("/", response_model=schemas.Term)
def create_term(
    *,
    db: Session = Depends(deps.get_db),
    term_in: schemas.TermCreate,
    current_admin: models.Admin = Depends(deps.get_current_active_admin_with_permission("term")),
) -> Any:

    if crud.term.get_by_details(
        db,
        name=term_in.name,
        year_id=term_in.year_id,
        current_year_term=term_in.current_year_term,
        start_date=term_in.start_date,
        end_date=term_in.end_date,
    ):
        raise HTTPException(
            status_code=409,
            detail="The term with these details already exists in the system!",
        )

    return crud.term.create(db, obj_in=term_in)


@router.put("/{term_id}", response_model=schemas.Term)
def update_term(
    *,
    db: Session = Depends(deps.get_db),
    term_id: int,
    term_in: schemas.TermUpdate,
    current_admin: models.Admin = Depends(deps.get_current_active_admin_with_permission("term")),
) -> Any:
    if term := crud.term.get(db, term_id):
        return crud.term.update(db, db_obj=term, obj_in=term_in)
    raise HTTPException(status_code=404, detail="The term with this ID does not exist in the system!")


@router.delete("/{term_id}")
def delete_term(
    *,
    db: Session = Depends(deps.get_db),
    term_id: int,
    current_admin: models.Admin = Depends(deps.get_current_active_admin_with_permission("term")),
) -> Any:
    if crud.term.get(db, term_id):
        return crud.term.remove(db, id=term_id)
    raise HTTPException(status_code=404, detail="The term with this ID does not exist in the system!")
