import json
import os

import boto3

from src.utils.password_utils import verify_password
from src.utils.utils import build_response
from src.validators.user_validation import SignIn
from src.utils.decorators import error_handler


TABLE_NAME = os.environ.get("TABLE_NAME")


@error_handler
def api(event, context):
    dynamodb = boto3.resource("dynamodb")
    table = dynamodb.Table(TABLE_NAME)

    body = json.loads(event["body"]) if event.get("body") else {}
    email = body.get("email")
    password = body.get("password")

    # Validation
    SignIn(**body)

    # Query user with email
    user_exists = table.query(
        IndexName="email",
        Limit=1,
        KeyConditionExpression="#sk = :sk and #email = :email",
        ExpressionAttributeNames={"#sk": "sk", "#email": "email"},
        ExpressionAttributeValues={":sk": "USER", ":email": email},
    ).get("Items")

    user = user_exists[0] if len(user_exists) else None
    if not user:
        return build_response(
            400, {"message": f"User with email: `{email}` doesn't exists"}
        )

    # Check account
    valid = verify_password(password, user.get("password").value)

    return (
        build_response(200, {"token": user.get("token")})
        if valid
        else build_response(400, {"message": "Invalid email or password"})
    )
