from typing import Optional

from pydantic import BaseModel


class StudentDivisionBase(BaseModel):
    student_id: Optional[str] = None
    division_id: Optional[str] = None
    batch_number: Optional[int] = None


class StudentDivisionCreate(StudentDivisionBase):
    student_id: str
    division_id: str


class StudentDivisionUpdate(StudentDivisionBase):
    ...
