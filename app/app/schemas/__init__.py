from .course import Course, CourseCreate, CourseUpdate
from .msg import Msg
from .school import School, SchoolCreate, SchoolUpdate
from .term import Term, TermCreate, TermInDB, TermUpdate
from .token import Token, TokenPayload
from .users.admin import Admin, AdminCreate, AdminPermissions, AdminRemove, AdminUpdate
from .users.professor import Professor, ProfessorCreate, ProfessorRemove, ProfessorUpdate
from .users.student import Student, StudentCreate, StudentRemove, StudentUpdate
from .users.user import User, UserCreate, UserInDB, UserUpdate
from .year import Year, YearCreate, YearInDB, YearUpdate
