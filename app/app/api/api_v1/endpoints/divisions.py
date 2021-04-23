import logging
from collections import defaultdict
from typing import Any, Dict, List

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app import crud, models, schemas
from app.api import deps
from app.exceptions import ConflictException, ForbiddenException, NotFoundException
from app.schemas import AdminPermissions

router = APIRouter()


@router.get("/", response_model=List[schemas.Division])
def read_divisions(
    db: Session = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100,
    _: models.Admin = Depends(deps.get_current_admin_with_permission("course")),
) -> Any:
    return crud.division.get_multi(db, skip=skip, limit=limit)


@router.get("/{division_id}", response_model=schemas.Division)
def read_division_by_id(
    *,
    db: Session = Depends(deps.get_db),
    division_id: str,
    _: models.Admin = Depends(deps.get_current_admin_with_permission("course")),
) -> Any:
    if division := crud.division.get(db, id=division_id):
        return division
    raise NotFoundException(detail="The division with this ID does not exist!")


@router.get("/{division_id}/students", response_model=List[schemas.Student])
def read_division_students_by_id(
    division_id: str, current_user: models.User = Depends(deps.get_current_user), db: Session = Depends(deps.get_db)
) -> Any:
    """
    Get all students for a specific division by ID.
    """
    # Fetch division with the corresponding ID from DB
    if division := crud.division.get(db, id=division_id):
        # Return the fetched object if current_user is the professor for the division
        # or admin with required perms
        if current_user.id == division.professor_id or (
            (admin := crud.admin.get(db, id=current_user.id))
            and AdminPermissions(admin.permissions).is_allowed("course")
        ):
            return list(division.students)

        raise ForbiddenException(detail="The user doesn't have enough privileges")

    raise NotFoundException(
        detail="The division with this ID does not exist in the system",
    )


@router.get("/{division_id}/students/{batch_number}", response_model=List[schemas.Student])
def read_division_batch_students_by_id(
    division_id: str,
    batch_number: int,
    current_user: models.User = Depends(deps.get_current_user),
    db: Session = Depends(deps.get_db),
) -> Any:
    """
    Get all students for a specific division by ID.
    """
    # Fetch division with the corresponding ID from DB
    if division := crud.division.get(db, id=division_id):
        # Return the fetched object if current_user is the professor for the division
        # or admin with required perms
        if current_user.id == division.professor_id or (
            (admin := crud.admin.get(db, id=current_user.id))
            and AdminPermissions(admin.permissions).is_allowed("course")
        ):
            return [
                student_division.student
                for student_division in getattr(division, "student_division")
                if student_division.batch_number == batch_number
            ]

        raise ForbiddenException(detail="The user doesn't have enough privileges")

    raise NotFoundException(
        detail="The division with this ID does not exist in the system",
    )


@router.post("/", response_model=schemas.Division)
def create_division(
    *,
    db: Session = Depends(deps.get_db),
    division_in: schemas.DivisionCreate,
    current_admin: models.Admin = Depends(deps.get_current_admin_with_permission("course")),
) -> Any:
    if crud.division.get_by_details(db, course_id=division_in.course_id, division_code=division_in.division_code):
        raise ConflictException(
            detail="The division with these details already exists in the system!",
        )

    logging.info(
        f"Admin {current_admin.user_id} ({current_admin.user.email}) is creating Division {division_in.__dict__}"
    )
    return crud.division.create(db, obj_in=division_in)


@router.post("/{division_id}/students", response_model=Dict[str, Any], status_code=207)
def add_division_students_by_id(
    *,
    db: Session = Depends(deps.get_db),
    division_id: str,
    user_ids: List[str],
    _: models.Admin = Depends(deps.get_current_admin_with_permission("course")),
) -> Any:
    if division := crud.division.get(db, id=division_id):
        response: Dict[str, Any] = defaultdict(lambda: [])
        errors = defaultdict(lambda: [])

        for user_id in user_ids:
            if user := crud.user.get(db, id=user_id):
                if user.type == "student":
                    if user.school_id == division.course.term.year.school_id:
                        if student := crud.student.get(db, id=user_id):
                            if student.term_id == division.course.term_id:
                                division.students.append(student)
                                response["success"].append(student.user_id)
                            else:
                                errors["different terms"].append(user_id)
                        else:
                            errors["no student object"].append(user_id)
                    else:
                        errors["different schools"].append(user_id)
                else:
                    errors["not a student"].append(user_id)
            else:
                errors["not a user"].append(user_id)

        # commit all the students added to the student
        db.commit()

        if errors.keys():
            response["errors"] = errors
        return response

    raise NotFoundException(detail="The division with this ID does not exist!")


@router.put("/{division_id}", response_model=schemas.Division)
def update_division(
    *,
    db: Session = Depends(deps.get_db),
    division_id: str,
    division_in: schemas.DivisionUpdate,
    current_admin: models.Admin = Depends(deps.get_current_admin_with_permission("course")),
) -> Any:
    if division := crud.division.get(db, id=division_id):
        logging.info(
            f"Admin {current_admin.user_id} ({current_admin.user.email}) is updating Division {division.id} "
            f"({division.course.name} - {division.division_code} for Term {division.course.name}) "
            f"to {division_in.__dict__}"
        )
        return crud.division.update(db, db_obj=division, obj_in=division_in)
    raise NotFoundException(detail="The division with this ID does not exist in the system!")


@router.delete("/{division_id}")
def delete_division(
    *,
    db: Session = Depends(deps.get_db),
    division_id: str,
    current_admin: models.Admin = Depends(deps.get_current_admin_with_permission("course")),
) -> Any:
    if division := crud.division.get(db, id=division_id):
        logging.info(
            f"Admin {current_admin.user_id} ({current_admin.user.email}) is deleting Division {division.id} "
            f"({division.course.name} - {division.division_code} for Term {division.course.name})"
        )
        return crud.division.remove(db, id=division_id)
    raise NotFoundException(detail="The division with this ID does not exist in the system!")
