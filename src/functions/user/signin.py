import boto3
import json
from src.utils.password_utils import verify_password

from src.utils.utils import build_response


def api(event, context):
    dynamodb = boto3.resource("dynamodb")
    table = dynamodb.Table("alakazam")

    body = json.loads(event["body"])
    email = body.get("email")
    password = body.get("password")

    # Validations
    if not email or not password:
        return build_response(400, "All fields are required")

    user = table.get_item(Key={"pk": email, "sk": "USER"}).get("Item")
    if not user:
        return build_response(
            400, f"User with email: `{email}` doesn't exists"
        )

    # Check account
    valid = verify_password(password, user.get("password").value)

    return (
        {
            "statusCode": 200,
            "body": json.dumps({"token": user.get("token")}),
        }
        if valid
        else build_response(400, "Invalid email or password")
    )
