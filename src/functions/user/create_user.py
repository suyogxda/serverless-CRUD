import boto3
import json
import uuid
from datetime import datetime, timezone
from src.utils.password_utils import hash_password
from src.utils.utils import build_response


# Currently storing as an variable, migrate to env later
TABLE_NAME = "alakazam"


def api(event, context):
    dynamodb = boto3.resource("dynamodb")
    table = dynamodb.Table(TABLE_NAME)

    body = json.loads(event["body"])
    email = body.get("email")
    name = body.get("name")
    password = body.get("password")
    repassword = body.get("repassword")

    # Validations
    if not (email and name and password and repassword):
        return build_response(400, "All fields are required")
    if password != repassword:
        return build_response(400, "Passwords don't match")
    user_exists = table.get_item(Key={"pk": email, "sk": "USER"}).get("Item")
    if user_exists:
        return build_response(
            400, f"User with email: `{email}` already exists"
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
    return {
        "statusCode": 201,
        "body": json.dumps({"message": f"User with email: `{email}` created"}),
    }
