# Import all the models, so that Base has them before being
# imported by Alembic
from app.db.base_class import Base  # noqa
from app.models.school import School  # noqa
from app.models.users.admin import Admin  # noqa
from app.models.users.user import User  # noqa
