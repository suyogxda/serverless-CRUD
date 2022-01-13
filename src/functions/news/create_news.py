import json
import os
import uuid
from datetime import datetime, timezone

import boto3

from src.utils.decorators import error_handler, auth_handler
from src.utils.utils import build_response
from src.validators.news_validation import CreateNews


TABLE_NAME = os.environ.get("TABLE_NAME")


@error_handler
@auth_handler
def api(event, context):
    dynamodb = boto3.resource("dynamodb")
    table = dynamodb.Table(TABLE_NAME)

    body = json.loads(event["body"])
    user = event.get("auth-user")

    # Validation
    CreateNews(**body)

    # Insert into db
    news_id = f"NEWS#{uuid.uuid4()}"
    table.put_item(
        Item={
            "pk": news_id,
            "sk": user,
            "title": body.get("title"),
            "created_at": int(datetime.now(timezone.utc).timestamp()),
            "description": body.get("description"),
        }
    )

    return build_response(
        201, {"message": f"News cerated with id `{news_id}`"}
    )
