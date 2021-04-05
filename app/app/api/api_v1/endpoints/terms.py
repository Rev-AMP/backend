import logging
from typing import Any, List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app import crud, models, schemas
from app.api import deps
from app.exceptions import ConflictException, NotFoundException
from app.schemas import StudentUpdate

router = APIRouter()


@router.get("/", response_model=List[schemas.Term])
def read_terms(
    db: Session = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100,
    _: models.Admin = Depends(deps.get_current_admin_with_permission("term")),
) -> Any:
    terms = crud.term.get_multi(db, skip=skip, limit=limit)
    return terms


@router.get("/{term_id}", response_model=schemas.Term)
def read_term_by_id(
    *,
    db: Session = Depends(deps.get_db),
    term_id: int,
    _: models.Admin = Depends(deps.get_current_admin_with_permission("term")),
) -> Any:
    if term := crud.term.get(db, term_id):
        return term
    raise NotFoundException(detail="The term with this ID does not exist!")


@router.get("/{term_id}/students", response_model=List[schemas.Student])
def read_term_students_by_id(
    *,
    db: Session = Depends(deps.get_db),
    term_id: int,
    _: models.Admin = Depends(deps.get_current_admin_with_permission("term")),
) -> Any:
    if term := crud.term.get(db, term_id):
        return term.students
    raise NotFoundException(detail="The term with this ID does not exist!")


@router.post("/{term_id}/students", response_model=List[schemas.Student])
def add_term_students_by_id(
    *,
    db: Session = Depends(deps.get_db),
    term_id: int,
    user_ids: List[int],
    _: models.Admin = Depends(deps.get_current_admin_with_permission("term")),
) -> Any:
    if term := crud.term.get(db, id=term_id):
        errors = []

        for user_id in user_ids:
            if user := crud.user.get(db, id=user_id):
                if user.type == "student":
                    if user.school_id == term.year.school_id:
                        if student := crud.student.get(db, id=user_id):
                            crud.student.update(db, db_obj=student, obj_in=StudentUpdate(term_id=term_id))
                        else:
                            errors.append(
                                {
                                    "msg": "no student object",
                                    "type": "user.no_student_object",
                                    "loc": ["user ID", user_id],
                                }
                            )
                    else:
                        errors.append(
                            {
                                "msg": "different schools",
                                "type": "objects.different_school",
                                "loc": ["user ID", user_id],
                            }
                        )
                else:
                    errors.append(
                        {
                            "msg": "not a student",
                            "type": "user.not_a_student",
                            "loc": ["user ID", user_id],
                        }
                    )
            else:
                errors.append(
                    {
                        "msg": "not a user",
                        "type": "user.not_a_user",
                        "loc": ["user ID", user_id],
                    }
                )

        if errors:
            raise HTTPException(status_code=418, detail=errors)

        db.refresh(term)
        return term.students

    raise NotFoundException(detail="The term with this ID does not exist!")


@router.post("/", response_model=schemas.Term)
def create_term(
    *,
    db: Session = Depends(deps.get_db),
    term_in: schemas.TermCreate,
    current_admin: models.Admin = Depends(deps.get_current_admin_with_permission("term")),
) -> Any:

    if crud.term.get_by_details(
        db,
        name=term_in.name,
        year_id=term_in.year_id,
        current_year_term=term_in.current_year_term,
        start_date=term_in.start_date,
        end_date=term_in.end_date,
    ):
        raise ConflictException(
            detail="The term with these details already exists in the system!",
        )
    logging.info(f"Admin {current_admin.user_id} ({current_admin.user.email}) is creating Term {term_in.__dict__}")

    return crud.term.create(db, obj_in=term_in)


@router.put("/{term_id}", response_model=schemas.Term)
def update_term(
    *,
    db: Session = Depends(deps.get_db),
    term_id: int,
    term_in: schemas.TermUpdate,
    current_admin: models.Admin = Depends(deps.get_current_admin_with_permission("term")),
) -> Any:
    if term := crud.term.get(db, term_id):
        logging.info(
            f"Admin {current_admin.user_id} ({current_admin.user.email}) is updating Term {term.id} ({term.name}) to"
            f" {term_in.__dict__}"
        )
        return crud.term.update(db, db_obj=term, obj_in=term_in)
    raise NotFoundException(detail="The term with this ID does not exist in the system!")


@router.delete("/{term_id}")
def delete_term(
    *,
    db: Session = Depends(deps.get_db),
    term_id: int,
    current_admin: models.Admin = Depends(deps.get_current_admin_with_permission("term")),
) -> Any:
    if term := crud.term.get(db, term_id):
        logging.info(
            f"Admin {current_admin.user_id} ({current_admin.user.email}) is deleting Term {term.id} ({term.id})"
        )
        return crud.term.remove(db, id=term_id)
    raise NotFoundException(detail="The term with this ID does not exist in the system!")
