import json
import uuid
from datetime import datetime, timezone

import boto3

from src.utils.decorators import error_handler
from src.utils.password_utils import hash_password
from src.utils.utils import build_response
from src.validators.user_validation import CreateUser

# Currently storing as an variable, migrate to env later
TABLE_NAME = "alakazam"


@error_handler
def api(event, context):
    dynamodb = boto3.resource("dynamodb")
    table = dynamodb.Table(TABLE_NAME)

    body = json.loads(event["body"])
    email = body.get("email")
    password = body.get("password")

    # Validations
    CreateUser(**body)
    user_exists = table.get_item(Key={"pk": email, "sk": "USER"}).get("Item")
    if user_exists:
        return build_response(
            400, {"message": f"User with email: `{email}` already exists"}
        )

    # Store to db if user doesn't exist
    table.put_item(
        Item={
            "pk": email,
            "sk": "USER",
            "created_at": str(datetime.now(timezone.utc)),
            "password": hash_password(password),
            "token": uuid.uuid4().hex,
        }
    )
    return build_response(
        201, {"message": f"User with email: `{email}` created"}
    )
