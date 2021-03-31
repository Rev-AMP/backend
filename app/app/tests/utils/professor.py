from sqlalchemy.orm import Session

from app import crud
from app.models.users.professor import Professor
from app.tests.utils.user import create_random_user


def create_random_professor(db: Session) -> Professor:
    user = create_random_user(db, type="professor")
    professor = crud.professor.get(db, id=user.id)
    assert professor
    return professor
