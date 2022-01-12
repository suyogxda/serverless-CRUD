import json

from pydantic import ValidationError

from src.errors.generic_error import GenericError


def error_handler(func):
    def validate(*args, **kwargs):
        try:
            to_return = func(*args, **kwargs)
        except ValidationError as e:
            return {
                "statusCode": 400,
                "body": e.json(),
            }
        except GenericError as e:
            return e.serialize_response()
        return to_return

    return validate
