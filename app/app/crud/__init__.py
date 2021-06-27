from .crud_admin import admin
from .crud_course import course
from .crud_division import division
from .crud_lecture import lecture
from .crud_professor import professor
from .crud_school import school
from .crud_student import student
from .crud_term import term
from .crud_timeslot import timeslot
from .crud_user import user
from .crud_year import year

# For a new basic set of CRUD operations you could just do

# from .base import CRUDBase
# from app.models.item import Item
# from app.schemas.item import ItemCreate, ItemUpdate

# item = CRUDBase[Item, ItemCreate, ItemUpdate](Item)
