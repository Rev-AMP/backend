import random
import string
from datetime import date, time
from typing import Any, Dict, Optional

from fastapi.testclient import TestClient
from sqlalchemy.ext.declarative import DeclarativeMeta
from sqlalchemy.schema import Table

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


def get_superuser_token_headers(client: TestClient, type_: str = "access") -> Dict[str, str]:
    login_data = {
        "username": settings.FIRST_SUPERUSER,
        "password": settings.FIRST_SUPERUSER_PASSWORD,
    }
    r = client.post(f"{settings.API_V1_STR}/login/access-token", data=login_data)
    tokens = r.json()
    a_token = tokens["access_token"] if type_ == "access" else tokens["refresh_token"]
    headers = {"Authorization": f"Bearer {a_token}"}
    return headers


def to_json(obj: Any, show_relations: Optional[bool] = True) -> Dict:
    # To store the table of the Object for which this function was called
    original_table: Table = obj.__table__

    def obj_to_json(obj: Any, show_relations: Optional[bool] = True, backref: Optional[Table] = None) -> Dict:
        result = {}
        for attr, column in obj.__mapper__.c.items():
            value = getattr(obj, attr)
            # Convert to ISO8601 format if date or time
            if isinstance(value, date) or isinstance(value, time):
                value = value.isoformat()
            result[column.key] = value

        if show_relations and len(obj.__mapper__.relationships.items()) != 0:
            for attr, relation in obj.__mapper__.relationships.items():
                # Avoid recursive loop between two tables.
                if relation.target in (backref, original_table):
                    continue

                value = getattr(obj, attr)
                if value is None:
                    result[relation.key] = None
                elif isinstance(value.__class__, DeclarativeMeta):
                    result[relation.key] = obj_to_json(obj=value, backref=obj.__table__)
                else:
                    result[relation.key] = [obj_to_json(obj=i, backref=obj.__table__) for i in value]
        return result

    return obj_to_json(obj=obj, show_relations=show_relations)


def compare_api_and_db_query_results(api_result: Dict, db_dict: Dict) -> None:
    """
    Compare whether the value of all the keys in the API call result are the same as the value of those keys in the DB
    query result
    """
    for key, value in api_result.items():
        if isinstance(value, dict) and isinstance(db_dict[key], dict):
            compare_api_and_db_query_results(value, db_dict[key])
        else:
            assert value == db_dict[key]
