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


@router.post("/{course_id}", response_model=schemas.File)
def upload_file(
    *,
    db: Session = Depends(deps.get_db),
    file: UploadFile = File(...),
    current_user: models.User = Depends(deps.get_current_user),
    course_id: str,
) -> Any:
    """
    Update a user's profile picture
    """
    if file.content_type != "application/pdf":
        raise UnsupportedMediaTypeException(detail="Profile pictures can only be PNG or JPG images")

    filename = save_file(file)
    return crud.file.create(
        db, obj_in=schemas.FileCreate(owner_id=current_user.id, course_id=course_id, filename=filename)
    )
