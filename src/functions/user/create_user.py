import json
import os
import uuid
from datetime import datetime, timezone

import boto3

from src.utils.decorators import error_handler
from src.utils.password_utils import hash_password
from src.utils.utils import build_response
from src.validators.user_validation import CreateUser

# Currently storing as an variable, migrate to env later
TABLE_NAME = os.environ.get("TABLE_NAME")


@error_handler
def api(event, context):
    dynamodb = boto3.resource("dynamodb")
    table = dynamodb.Table(TABLE_NAME)

    body = json.loads(event["body"])
    email = body.get("email")
    password = body.get("password")

    # Validations
    CreateUser(**body)
    user_exists = table.query(
        IndexName="email",
        Limit=1,
        KeyConditionExpression="#sk = :sk and #email = :email",
        ExpressionAttributeNames={"#sk": "sk", "#email": "email"},
        ExpressionAttributeValues={":sk": "USER", ":email": email},
    ).get("Item")
    if user_exists:
        return build_response(
            400, {"message": f"User with email: `{email}` already exists"}
        )

    # Store to db if user doesn't exist
    user_id = uuid.uuid4()
    _items = [
        {
            "pk": f"USER#{user_id}",
            "sk": "USER",
            "created_at": int(datetime.now(timezone.utc).timestamp()),
            "password": hash_password(password),
        },
        {
            "pk": f"TOKEN#{uuid.uuid4().hex}",
            "sk": "TOKEN",
            "created_at": int(datetime.now(timezone.utc).timestamp()),
            "user": f"USER#{user_id}",
        },
    ]
    with table.batch_writer() as batch:
        [batch.put_item(Item=_item) for _item in _items]

    return build_response(
        201, {"message": f"User with email: `{email}` created"}
    )
