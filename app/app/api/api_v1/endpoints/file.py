from typing import Any, List, Optional

from fastapi import APIRouter, Depends, File, UploadFile
from sqlalchemy.orm import Session

from app import crud, models, schemas
from app.api import deps
from app.exceptions import (
    BadRequestException,
    ForbiddenException,
    NotFoundException,
    UnsupportedMediaTypeException,
)
from app.utils import save_file

router = APIRouter()


@router.get("/", response_model=List[schemas.File])
def get_all_files_user(
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_non_admin_user),
) -> Any:
    """
    Retrieve files.
    """
    return crud.file.get_by_owner(db, owner_id=current_user.id)


@router.get("/course", response_model=List[schemas.File])
def get_all_files_course(
    *,
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_non_admin_user),
    course_id: str,
) -> Any:
    """
    Retrieve files.
    """
    if current_user.type == "student" and (student := crud.student.get(db, id=current_user.id)):
        courses = (division.course_id for division in student.divisions)
    elif current_user.type == "professor" and (professor := crud.professor.get(db, id=current_user.id)):
        courses = (division.course_id for division in professor.divisions)
    else:
        raise BadRequestException(detail=f"Could not fetch courses for user {current_user.id}")
    return [
        file
        for file in crud.file.get_by_course(db, course_id=course_id)
        if file.file_type in ("assignment", "material")
        for course_id in courses
    ]


@router.get("/{file_id}", response_model=schemas.File)
def get_file_by_id(
    *,
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_non_admin_user),
    file_id: str,
) -> Any:
    """
    Retrieve a file by id
    """
    if file := crud.file.get(db, id=file_id):
        if current_user.id == file.owner_id or (
            current_user.type == "professor"
            and (
                (professor := crud.professor.get(db, id=current_user.id))
                and file.course_id in (division.course_id for division in professor.divisions)
            )
        ):
            return file
    raise BadRequestException(detail=f"File with id {file_id} not found or you don't have access to it")


@router.get("/submission/{submission_id}", response_model=List[schemas.File])
def get_file_by_submission(
    *,
    db: Session = Depends(deps.get_db),
    current_professor: models.Professor = Depends(deps.get_current_professor),
    submission_id: str,
) -> Any:
    """
    Retrieve a file by id
    """
    if file := crud.file.get(db, id=submission_id):
        if file.course_id in {division.course_id for division in current_professor.divisions}:
            return file
    raise NotFoundException(detail=f"Assignment with id {submission_id} not found or you don't have access to it")


@router.post("/{course_id}", response_model=schemas.File)
def upload_file(
    *,
    db: Session = Depends(deps.get_db),
    file: UploadFile = File(...),
    current_user: models.User = Depends(deps.get_current_non_admin_user),
    course_id: str,
    file_type: str,
    submission_id: Optional[str] = None,
) -> Any:
    """
    Update a user's profile picture
    """

    if current_user.type == "student" and (student := crud.student.get(db, id=current_user.id)):
        courses = (division.course_id for division in student.divisions)
    elif current_user.type == "professor" and (professor := crud.professor.get(db, id=current_user.id)):
        courses = (division.course_id for division in professor.divisions)
    else:
        raise BadRequestException(detail=f"Could not upload file for course {course_id}")

    if course_id not in courses:
        raise ForbiddenException(detail="You can't upload files for this course!")

    if file.content_type != "application/pdf":
        raise UnsupportedMediaTypeException(detail="Uploaded files can only be PDFs")

    if submission_id:
        if assignment := crud.file.get(db, id=submission_id):
            if assignment.file_type != "assignment":
                raise BadRequestException(detail=f"File {submission_id} isn't an assignment!")
        else:
            raise NotFoundException(detail=f"Assignment with id {submission_id} not found!")
        if file_type != "submission":
            raise BadRequestException(detail=f"File with type {file_type} can't be submitted")

    filename = save_file(file)
    return crud.file.create(
        db,
        obj_in=schemas.FileCreate(
            owner_id=current_user.id,
            course_id=course_id,
            filename=filename,
            file_type=file_type,
            submission_id=submission_id,
        ),
    )


@router.put("/{file_id}", response_model=schemas.File)
def update_file(
    *,
    db: Session = Depends(deps.get_db),
    file_id: str,
    file_in: schemas.FileUpdate,
    current_professor: models.Professor = Depends(deps.get_current_professor),
) -> Any:
    """
    Update the attributes of an uploaded file (basically grade an assignment)
    """
    if file := crud.file.get(db, id=file_id):
        if file.course_id in {division.course_id for division in current_professor.divisions}:
            if file.file_type == "submission":
                return crud.file.update(db, db_obj=file, obj_in=file_in)
            raise BadRequestException(detail=f"Cannot update a file of type {file.file_type}")
    raise NotFoundException(detail=f"Assignment with id {file_id} not found or you don't have access to it")
