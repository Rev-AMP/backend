from typing import Any, List

from fastapi import APIRouter, Depends, File, UploadFile
from sqlalchemy.orm import Session

from app import crud, models, schemas
from app.api import deps
from app.exceptions import NotFoundException, UnsupportedMediaTypeException
from app.utils import save_file

router = APIRouter()


@router.get("/", response_model=List[schemas.File])
def get_all_files_user(
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_user),
) -> Any:
    """
    Retrieve files.
    """
    return crud.file.get_by_owner(db, owner_id=current_user.id)


@router.get("/{course_id}", response_model=List[schemas.File])
def get_all_files_course(
    *,
    db: Session = Depends(deps.get_db),
    _: models.User = Depends(deps.get_current_user),
    course_id: str,
) -> Any:
    """
    Retrieve files.
    """
    return crud.file.get_by_course(db, course_id=course_id)


@router.get("/{file_id}", response_model=schemas.File)
def get_file_by_id(
    *,
    db: Session = Depends(deps.get_db),
    file_id: str,
) -> Any:
    """
    Retrieve a file by id
    """
    if file := crud.file.get(db, id=file_id):
        return file
    raise NotFoundException(detail=f"File with id {file_id} not found")


@router.get("/{submission_id}", response_model=List[schemas.File])
def get_file_by_submission(
    *,
    db: Session = Depends(deps.get_db),
    submission_id: str,
) -> Any:
    """
    Retrieve a file by id
    """
    if crud.file.get(db, id=submission_id):
        return crud.file.get_by_submission(db, submission_id=submission_id)
    raise NotFoundException(detail=f"Assignment with id {submission_id} not found")


@router.post("/{course_id}", response_model=schemas.File)
def upload_file(
    *,
    db: Session = Depends(deps.get_db),
    file: UploadFile = File(...),
    current_user: models.User = Depends(deps.get_current_user),
    course_id: str,
    file_type: str,
) -> Any:
    """
    Update a user's profile picture
    """
    if file.content_type != "application/pdf":
        raise UnsupportedMediaTypeException(detail="Uploaded files can only be PDFs")

    filename = save_file(file)
    return crud.file.create(
        db,
        obj_in=schemas.FileCreate(
            owner_id=current_user.id, course_id=course_id, filename=filename, file_type=file_type
        ),
    )


@router.put("/{file_id}", response_model=schemas.File)
def update_file(
    *,
    db: Session = Depends(deps.get_db),
    file_id: str,
    file_in: schemas.FileUpdate,
) -> Any:
    """
    Update the attributes of an uploaded file (basically grade an assignment)
    """
    if file := crud.file.get(db, id=file_id):
        return crud.file.update(db, db_obj=file, obj_in=file_in)
