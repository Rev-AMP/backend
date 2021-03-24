import logging
from typing import Any, List

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app import crud, models, schemas
from app.api import deps
from app.exceptions import ConflictException, NotFoundException

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
    raise NotFoundException(detail="The course with this ID does not exist!")


@router.post("/", response_model=schemas.Course)
def create_course(
    *,
    db: Session = Depends(deps.get_db),
    course_in: schemas.CourseCreate,
    current_admin: models.Admin = Depends(deps.get_current_active_admin_with_permission("course")),
) -> Any:

    if crud.course.get_by_details(
        db, name=course_in.name, course_code=course_in.course_code, panel_code=course_in.panel_code, term_id=course_in.term_id
    ):
        raise ConflictException(
            detail="The course with these details already exists in the system!",
        )

    logging.info(f"Admin {current_admin.user_id} ({current_admin.user.email}) is creating Course {course_in.__dict__}")
    return crud.course.create(db, obj_in=course_in)


@router.put("/{course_id}", response_model=schemas.Course)
def update_course(
    *,
    db: Session = Depends(deps.get_db),
    course_id: int,
    course_in: schemas.CourseUpdate,
    current_admin: models.Admin = Depends(deps.get_current_active_admin_with_permission("course")),
) -> Any:
    if course := crud.course.get(db, id=course_id):
        logging.info(
            f"Admin {current_admin.user_id} ({current_admin.user.email}) is updating Course {course.id}({course.name}) "
            f"to {course_in.__dict__}"
        )
        return crud.course.update(db, db_obj=course, obj_in=course_in)
    raise NotFoundException(detail="The course with this ID does not exist in the system!")


@router.delete("/{course_id}")
def delete_course(
    *,
    db: Session = Depends(deps.get_db),
    course_id: int,
    current_admin: models.Admin = Depends(deps.get_current_active_admin_with_permission("course")),
) -> Any:
    if course := crud.course.get(db, id=course_id):
        logging.info(
            f"Admin {current_admin.user_id} ({current_admin.user.email}) is deleting Course {course.id} ({course.name})"
        )
        return crud.course.remove(db, id=course_id)
    raise NotFoundException(detail="The course with this ID does not exist in the system!")
