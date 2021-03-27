from typing import Optional

from sqlalchemy.orm import Session

from app import crud
from app.models.users.student import Student
from app.schemas import StudentUpdate
from app.tests.utils.term import create_random_term
from app.tests.utils.user import create_random_user


def create_random_student(db: Session, term_id: Optional[int] = None) -> Student:
    user = create_random_user(db, type="student")
    if term_id and crud.term.get(db, id=term_id):
        student_in = StudentUpdate(user_id=user.id, term_id=term_id)
    else:
        term = create_random_term(db)
        student_in = StudentUpdate(user_id=user.id, term_id=term.id)
    student = crud.student.get(db, id=user.id)
    assert student
    return crud.student.update(db, db_obj=student, obj_in=student_in)
