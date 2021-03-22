import random
import string
from datetime import date
from typing import Any, Dict, Optional

from fastapi.testclient import TestClient
from sqlalchemy.ext.declarative import DeclarativeMeta

from app.core.config import settings


def random_lower_string() -> str:
    return "".join(random.choices(string.ascii_lowercase, k=32))


def random_password() -> str:
    return "".join(
        random.choices(string.ascii_lowercase, k=3)
        + random.choices(string.ascii_uppercase, k=3)
        + random.choices(string.digits, k=3),
    )


def random_email() -> str:
    return f"{random_lower_string()}@{random_lower_string()}.com"


def get_superuser_token_headers(client: TestClient, type_: str = 'access') -> Dict[str, str]:
    login_data = {
        "username": settings.FIRST_SUPERUSER,
        "password": settings.FIRST_SUPERUSER_PASSWORD,
    }
    r = client.post(f"{settings.API_V1_STR}/login/access-token", data=login_data)
    tokens = r.json()
    a_token = tokens["access_token"] if type_ == 'access' else tokens["refresh_token"]
    headers = {"Authorization": f"Bearer {a_token}"}
    return headers


def to_json(obj: Any, show_relations: Optional[bool] = True) -> Dict:
    if show_relations and len(obj.__mapper__.relationships.items()) == 0:
        show_relations = False

    result = {}
    for attr, column in obj.__mapper__.c.items():
        result[column.key] = value.isoformat() if isinstance(value := getattr(obj, attr), date) else value

    if show_relations:
        for attr, relation in obj.__mapper__.relationships.items():
            value = getattr(obj, attr)

            if value is None:
                result[relation.key] = None
            elif isinstance(value.__class__, DeclarativeMeta):
                result[relation.key] = to_json(value)
            else:
                result[relation.key] = [to_json(i) for i in value]
    return result
