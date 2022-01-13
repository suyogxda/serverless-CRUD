import json
import os

import boto3
from pydantic import ValidationError

from src.errors.generic_error import GenericError


TABLE_NAME = os.environ.get("TABLE_NAME")


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


def auth_handler(func):
    def validate(*args, **kwargs):
        event = args[0]
        args[0]["alakazam"] = "Alakazam"
        if not event or not event.get("headers"):
            raise GenericError("Authorization details not provided", 401)
        headers = event.get("headers", {})
        if headers.get("Authorization"):
            dynamodb = boto3.resource("dynamodb")
            table = dynamodb.Table(TABLE_NAME)
            _token = headers.get("Authorization")
            token = table.get_item(
                Key={"pk": f"TOKEN#{_token}", "sk": "TOKEN"}
            ).get("Item")
            if token:
                args[0]["auth-user"] = token.get("user")
                to_return = func(*args, **kwargs)
                return to_return
        raise GenericError("Unauthorized", 401)

    return validate
