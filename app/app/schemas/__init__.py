from .course import Course, CourseCreate, CourseUpdate
from .division import Division, DivisionCreate, DivisionUpdate
from .file import File, FileCreate, FileUpdate
from .lecture import Lecture, LectureCreate, LectureUpdate
from .msg import Msg
from .school import School, SchoolCreate, SchoolUpdate
from .term import Term, TermCreate, TermUpdate
from .timeslot import TimeSlot, TimeSlotCreate, TimeSlotUpdate
from .token import Token, TokenPayload
from .users.admin import Admin, AdminCreate, AdminPermissions, AdminRemove, AdminUpdate
from .users.professor import (
    Professor,
    ProfessorCreate,
    ProfessorRemove,
    ProfessorUpdate,
)
from .users.student import Student, StudentCreate, StudentRemove, StudentUpdate
from .users.user import User, UserCreate, UserUpdate
from .year import Year, YearCreate, YearUpdate
