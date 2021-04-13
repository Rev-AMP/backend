import logging
from typing import Any, List

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app import crud, models, schemas
from app.api import deps
from app.exceptions import ForbiddenException, NotFoundException
from app.schemas import AdminPermissions

router = APIRouter()


@router.get("/", response_model=List[schemas.Student])
def read_students(
    db: Session = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100,
    _: models.Admin = Depends(deps.get_current_admin_with_permission("student")),
) -> Any:
    """
    Retrieve students
    """
    return crud.student.get_multi(db, skip=skip, limit=limit)


@router.get("/me", response_model=schemas.Student)
def get_student_me(
    current_student: models.Student = Depends(deps.get_current_student),
) -> Any:
    """
    Get current student
    """
    return current_student


@router.get("/me/divisions", response_model=List[schemas.Division])
def get_student_divisions_me(
    current_student: models.Student = Depends(deps.get_current_student),
) -> Any:
    """
    Get current student divisions
    """
    return list(current_student.divisions)


@router.get("/{student_id}", response_model=schemas.Student)
def read_student_by_id(
    student_id: str, current_user: models.User = Depends(deps.get_current_user), db: Session = Depends(deps.get_db)
) -> Any:
    """
    Get a specific student by ID.
    """

    # Fetch student with the corresponding ID from DB
    student = crud.student.get(db, id=student_id)

    # Return the fetched object without checking perms if current_student is trying to fetch itself
    if current_user.id == student_id:
        return student

    # check perms and return if student exists, else 404
    if (admin := crud.admin.get(db, id=current_user.id)) and AdminPermissions(admin.permissions).is_allowed("student"):
        if student:
            return student
        raise NotFoundException(
            detail="The student with this ID does not exist in the system",
        )

    raise ForbiddenException(detail="The user doesn't have enough privileges")


@router.get("/{student_id}/divisions", response_model=List[schemas.Division])
def read_student_divisions_by_id(
    student_id: str, current_user: models.User = Depends(deps.get_current_user), db: Session = Depends(deps.get_db)
) -> Any:
    """
    Get a specific student's divisions by ID.
    """
    # Fetch student with the corresponding ID from DB
    if student := crud.student.get(db, id=student_id):
        # Return the fetched divisions if current_user is trying to fetch itself
        # or is an admin with the required perms
        if current_user.id == student_id or (
            (admin := crud.admin.get(db, id=current_user.id))
            and AdminPermissions(admin.permissions).is_allowed("student")
        ):
            return list(student.divisions)

        raise ForbiddenException(detail="The user doesn't have enough privileges")

    raise NotFoundException(
        detail="The student with this ID does not exist in the system",
    )


@router.put("/{student_id}", response_model=schemas.Student)
def update_student(
    *,
    db: Session = Depends(deps.get_db),
    student_id: str,
    student_in: schemas.StudentUpdate,
    current_admin: models.Admin = Depends(deps.get_current_admin_with_permission("student")),
) -> Any:
    """
    Update student.
    """

    if student := crud.student.get(db, id=student_id):
        logging.info(
            f"Admin {current_admin.user_id} ({current_admin.user.email}) is updating student {student.user_id}"
            f"({student.user.email}) to {student_in.__dict__}"
        )
        return crud.student.update(db, db_obj=student, obj_in=student_in)

    raise NotFoundException(
        detail="This student does not exist!",
    )
