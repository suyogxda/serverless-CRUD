import os

import boto3
from botocore.exceptions import ClientError
from pydantic import ValidationError

from src.errors.generic_error import GenericError
from src.utils.utils import build_response

TABLE_NAME = os.environ.get("TABLE_NAME")


def error_handler(func):
    """
    Decorator used to catch certain types of Exceptions
    """

    def validate(*args, **kwargs):
        try:
            to_return = func(*args, **kwargs)
        except ValidationError as e:
            return {
                "statusCode": 400,
                "body": e.json(),
            }
        except ClientError as e:
            if (
                e.response["Error"]["Code"]
                == "ConditionalCheckFailedException"
            ):
                return build_response(404, {"message": "Not found"})
            print("BAD_REQUEST", e)
            return build_response(400, {"message": "Bad Request"})
        except GenericError as e:
            return e.serialize_response()
        return to_return

    return validate


def auth_handler(func):
    """
    Decorator to verify if request is authenticated or not.
    For now, a simple random token is generated per user.
    The token doesn't have any expiration or other essential attributes.
    """

    def validate(*args, **kwargs):
        event = args[0]

        # Semd 401 if no auth header is present
        if not event or not event.get("headers"):
            raise GenericError("Authorization details not provided", 401)

        headers = event.get("headers", {})

        # Check auth if header is present
        if headers.get("Authorization"):
            dynamodb = boto3.resource("dynamodb")
            table = dynamodb.Table(TABLE_NAME)
            _token = headers.get("Authorization")

            # I've used a simple token mechanism so for now, just check if token is present
            token = table.get_item(
                Key={"pk": f"TOKEN#{_token}", "sk": "TOKEN"}
            ).get("Item")

            # If token is present, also pass dynamodb table instance...
            # ...as it's not necessary to initialize it again
            if token:
                args[0]["auth-user"] = token.get("user")
                args[0]["dynamodb-table"] = table
                to_return = func(*args, **kwargs)
                return to_return
        raise GenericError("Unauthorized", 401)

    return validate
