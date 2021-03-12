from typing import Any, List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app import crud, models, schemas
from app.api import deps

router = APIRouter()


@router.get("/", response_model=List[schemas.Course])
def read_courses(
    db: Session = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100,
    _: models.Admin = Depends(deps.get_current_active_admin_with_permission("course")),
) -> Any:
    return crud.course.get_multi(db, skip=skip, limit=limit)


@router.get("/{course_id}", response_model=schemas.Course)
def read_course_by_id(
    *,
    db: Session = Depends(deps.get_db),
    course_id: int,
    _: models.Admin = Depends(deps.get_current_active_admin_with_permission("course")),
) -> Any:
    if course := crud.course.get(db, id=course_id):
        return course
    raise HTTPException(status_code=404, detail="The course with this ID does not exist!")


@router.post("/", response_model=schemas.Course)
def create_course(
    *,
    db: Session = Depends(deps.get_db),
    course_in: schemas.CourseCreate,
    _: models.Admin = Depends(deps.get_current_active_admin_with_permission("course")),
) -> Any:

    if crud.course.get_by_details(db, name=course_in.name, code=course_in.code, term_id=course_in.term_id):
        raise HTTPException(
            status_code=409,
            detail="The course with these details already exists in the system!",
        )

    return crud.course.create(db, obj_in=course_in)


@router.put("/{course_id}", response_model=schemas.Course)
def update_course(
    *,
    db: Session = Depends(deps.get_db),
    course_id: int,
    course_in: schemas.CourseUpdate,
    _: models.Admin = Depends(deps.get_current_active_admin_with_permission("course")),
) -> Any:
    if course := crud.course.get(db, id=course_id):
        return crud.course.update(db, db_obj=course, obj_in=course_in)
    raise HTTPException(status_code=404, detail="The course with this ID does not exist in the system!")


@router.delete("/{course_id}")
def delete_course(
    *,
    db: Session = Depends(deps.get_db),
    course_id: int,
    _: models.Admin = Depends(deps.get_current_active_admin_with_permission("course")),
) -> Any:
    if crud.course.get(db, id=course_id):
        return crud.course.remove(db, id=course_id)
    raise HTTPException(status_code=404, detail="The course with this ID does not exist in the system!")
