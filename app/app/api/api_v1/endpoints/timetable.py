import calendar
from typing import Any, Dict, List

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app import crud, models
from app.api import deps
from app.exceptions import BadRequestException
from app.schemas import Lecture

router = APIRouter()


@router.get("/", response_model=Dict[str, List[Lecture]])
def get_timetable(
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_user),
) -> Any:
    if user := crud.user.get(db, id=current_user.id):
        if user.type == "student" and (student := crud.student.get(db, id=user.id)):
            return generate_timetable(db, student.divisions)
        elif user.type == "professor" and (professor := crud.professor.get(db, id=user.id)):
            return generate_timetable(db, professor.divisions)
        else:
            raise BadRequestException(detail=f"No timetable can be generated for user type {user.type}")
    raise BadRequestException(detail="User object not found!")


def generate_timetable(db: Session, divisions: List[str]) -> Dict:
    response = {}
    for day in calendar.day_name:
        for division_id in divisions:
            if lectures := crud.lecture.get_by_day_division(db, day=day, division_id=division_id):
                response[day] = lectures
    return response
