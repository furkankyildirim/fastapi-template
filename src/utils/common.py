import json
from typing import Dict
import re
from datetime import time


def json_serializer(obj: Dict, **kwargs) -> str:
    """

    Args:
        obj ():

    Returns:

    """
    obj = datetime_serializer(obj)
    return json.dumps(obj, default=str, **kwargs)


def datetime_serializer(obj: Dict) -> Dict:
    """

    Args:
        obj ():

    Returns:

    """
    for key, value in obj.items():
        if isinstance(value, dict):
            obj[key] = datetime_serializer(value)
        elif isinstance(value, list):
            obj[key] = [datetime_serializer(item) if isinstance(item, dict) else item for item in value]
        elif hasattr(value, 'isoformat'):
            obj[key] = value.isoformat()
        elif isinstance(value, time):
            obj[key] = value.strftime('%H:%M:%S')
    return obj


# Define a function to convert camel case to title case
def camel_to_title_case(text):
    if not text or not isinstance(text, str):
        return text
    return re.sub(r'([a-z])([A-Z])', r'\1 \2', text).title()


class Singleton(type):
    """
    Singleton metaclass.
    """

    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]


def email_validator(email: str) -> bool:
    """
    Email validator.

    Args:
        email (str): Email.

    Returns:
        bool: True if valid, False otherwise.
    """
    return bool(re.match(r"[^@]+@[^@]+\.[^@]+", email))


def format_validation_error(errors: list[dict[str, any]]) -> list[dict[str, any]]:
    """
    Format Pydantic errors to include specific constraint violations such as ge, le, gt, lt.
    """
    formatted_errors = []
    for error in errors:
        err = error.copy()
        loc = err.get("loc", [])
        msg = err.get("msg", "")
        if "value is not a valid integer" in msg or "value is not a valid float" in msg:
            constraint = "Invalid data type"
        elif "ensure this value is greater than or equal to" in msg:
            constraint = "Minimum value constraint violated (ge)"
        elif "ensure this value is less than or equal to" in msg:
            constraint = "Maximum value constraint violated (le)"
        elif "ensure this value is greater than" in msg:
            constraint = "Value must be greater than specified constraint (gt)"
        elif "ensure this value is less than" in msg:
            constraint = "Value must be less than specified constraint (lt)"
        else:
            constraint = msg
        formatted_errors.append({"location": loc, "constraint": constraint})
    return formatted_errors
