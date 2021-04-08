from sqlalchemy.orm import Session

from app import crud
from app.schemas import StudentUpdate
from app.tests.utils.student import create_random_student
from app.tests.utils.term import create_random_term


def test_create_student(db: Session) -> None:
    student = create_random_student(db)
    assert student
    assert student.user_id
    assert student.term_id


def test_update_user_student(db: Session) -> None:
    student = create_random_student(db)
    assert student
    term = create_random_term(db)
    student_update = StudentUpdate(user_id=student.user_id, term_id=term.id)
    crud.student.update(db, db_obj=student, obj_in=student_update)
    user_2 = crud.student.get(db, id=student.user_id)
    assert user_2
    assert user_2.term_id == term.id


def test_update_user_student_with_dict(db: Session) -> None:
    student = create_random_student(db)
    assert student
    term = create_random_term(db)
    student_update = {"user_id": student.user_id, "term_id": term.id}
    crud.student.update(db, db_obj=student, obj_in=student_update)
    student_2 = crud.student.get(db, id=student.user_id)
    assert student_2
    assert student_2.user_id == student.user_id
    assert student_2.term_id == term.id


def test_remove_student(db: Session) -> None:
    student = create_random_student(db)
    assert student
    crud.student.remove(db, id=student.user_id)
    assert not crud.student.get(db, id=student.user_id)
