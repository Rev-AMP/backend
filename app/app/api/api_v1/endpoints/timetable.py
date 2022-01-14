import calendar
from collections import defaultdict
from typing import Any, Dict

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app import crud, models
from app.api import deps
from app.exceptions import BadRequestException, NotFoundException
from app.models import Division
from app.schemas import Lecture

router = APIRouter()


@router.get("/", response_model=dict[str, list[Lecture]])
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


@router.get("/{division_id}", response_model=dict[str, list[Lecture]])
def get_timetable_division(
    *,
    db: Session = Depends(deps.get_db),
    _: models.User = Depends(deps.get_current_admin_with_permission("course")),
    division_id: str,
) -> Any:
    if division := crud.division.get(db, id=division_id):
        return generate_timetable(db, [division])
    raise NotFoundException(detail=f"Division with id {division_id} not found")


def generate_timetable(db: Session, divisions: list[Division]) -> Dict:
    response: Dict = defaultdict(lambda: [])
    for day in calendar.day_name:
        for division in divisions:
            if lectures := crud.lecture.get_by_day_division(db, day=day, division_id=division.id):
                response[day] += lectures
    return response
