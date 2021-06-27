import calendar
from typing import Any, Dict, List

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app import crud, models
from app.api import deps
from app.exceptions import NotFoundException
from app.schemas import Lecture

router = APIRouter()


@router.get("/{division_id}", response_model=Dict[str, List[Lecture]])
def get_timetable(
    division_id: str,
    db: Session = Depends(deps.get_db),
    _: models.User = Depends(deps.get_current_user),
) -> Any:
    response = {}
    if crud.division.get(db, id=division_id):
        for day in calendar.day_name:
            response[day] = crud.lecture.get_by_day_division(db, day=day, division_id=division_id)
        return [day for day in response if day]
    raise NotFoundException(detail=f"Division with id {division_id} not found")
