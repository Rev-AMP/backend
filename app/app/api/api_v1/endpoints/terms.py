import logging
from collections import defaultdict
from typing import Any, Dict, List

from fastapi import APIRouter, Depends
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
    term_id: str,
    _: models.Admin = Depends(deps.get_current_admin_with_permission("term")),
) -> Any:
    if term := crud.term.get(db, term_id):
        return term
    raise NotFoundException(detail="The term with this ID does not exist!")


@router.get("/{term_id}/students", response_model=List[schemas.Student])
def read_term_students_by_id(
    *,
    db: Session = Depends(deps.get_db),
    term_id: str,
    _: models.Admin = Depends(deps.get_current_admin_with_permission("term")),
) -> Any:
    if term := crud.term.get(db, term_id):
        return term.students
    raise NotFoundException(detail="The term with this ID does not exist!")


@router.post("/{term_id}/students", response_model=Dict[str, Any], status_code=207)
def add_term_students_by_id(
    *,
    db: Session = Depends(deps.get_db),
    term_id: str,
    user_ids: List[str],
    _: models.Admin = Depends(deps.get_current_admin_with_permission("term")),
) -> Any:
    if term := crud.term.get(db, id=term_id):
        response: Dict[str, Any] = defaultdict(lambda: [])
        errors = defaultdict(lambda: [])

        for user_id in user_ids:
            if user := crud.user.get(db, id=user_id):
                if user.type == "student":
                    if user.school_id == term.year.school_id:
                        if student := crud.student.get(db, id=user_id):
                            if student.term_id != term_id:
                                crud.student.update(db, db_obj=student, obj_in=StudentUpdate(term_id=term_id))
                                response["success"].append(student.user_id)
                            else:
                                errors["student already in term"].append(user_id)
                        else:
                            errors["no student object"].append(user_id)
                    else:
                        errors["different schools"].append(user_id)
                else:
                    errors["not a student"].append(user_id)
            else:
                errors["not a user"].append(user_id)

        if errors.keys():
            response["errors"] = errors
        return response

    raise NotFoundException(detail="The term with this ID does not exist!")


@router.delete("/{term_id}/students/{student_id}", response_model=schemas.Student)
def remove_student_from_term(
    *,
    db: Session = Depends(deps.get_db),
    term_id: str,
    student_id: str,
    current_admin: models.Admin = Depends(deps.get_current_admin_with_permission("term")),
) -> Any:

    if term := crud.term.get(db, term_id):
        if student := crud.student.get(db, student_id):
            logging.info(
                f"Admin {current_admin.user_id} ({current_admin.user.email}) is deleting Student {student_id} "
                f"({student.user.email}) from Term {term_id} ({term.name})"
            )
            return crud.student.update(db, db_obj=student, obj_in=StudentUpdate(term_id=None))
        raise NotFoundException(detail=f"Student with id {student_id} not found in term {term_id}")
    raise NotFoundException(detail=f"Term with id {term_id} not found")


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
    term_id: str,
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
    term_id: str,
    current_admin: models.Admin = Depends(deps.get_current_admin_with_permission("term")),
) -> Any:
    if term := crud.term.get(db, term_id):
        logging.info(
            f"Admin {current_admin.user_id} ({current_admin.user.email}) is deleting Term {term.id} ({term.id})"
        )
        return crud.term.remove(db, id=term_id)
    raise NotFoundException(detail="The term with this ID does not exist in the system!")
