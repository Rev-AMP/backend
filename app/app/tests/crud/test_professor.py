from sqlalchemy.orm import Session

from app import crud
from app.schemas import ProfessorUpdate
from app.tests.utils.professor import create_random_professor
from app.tests.utils.term import create_random_term


def test_create_professor(db: Session) -> None:
    professor = create_random_professor(db)
    assert professor
    assert professor.user_id


def test_update_user_professor(db: Session) -> None:
    professor = create_random_professor(db)
    assert professor
    term = create_random_term(db)
    professor_update = ProfessorUpdate(user_id=professor.user_id, term_id=term.id)
    crud.professor.update(db, db_obj=professor, obj_in=professor_update)
    user_2 = crud.professor.get(db, id=professor.user_id)
    assert user_2


def test_update_user_professor_with_dict(db: Session) -> None:
    professor = create_random_professor(db)
    assert professor
    term = create_random_term(db)
    professor_update = {"user_id": professor.user_id, "term_id": term.id}
    crud.professor.update(db, db_obj=professor, obj_in=professor_update)
    professor_2 = crud.professor.get(db, id=professor.user_id)
    assert professor_2
    assert professor_2.user_id == professor.user_id
