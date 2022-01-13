import json
import uuid
from datetime import datetime, timezone


from src.utils.decorators import error_handler, auth_handler
from src.utils.utils import build_response
from src.validators.news_validation import CreateNews


@error_handler
@auth_handler
def api(event, context):
    table = event.get("dynamodb-table")

    body = json.loads(event["body"])
    user = event.get("auth-user")

    # Validation
    CreateNews(**body)

    # Insert into db
    news_id = f"NEWS#{uuid.uuid4()}"
    table.put_item(
        Item={
            "pk": news_id,
            "sk": "NEWS",
            "title": body.get("title"),
            "created_at": int(datetime.now(timezone.utc).timestamp()),
            "description": body.get("description"),
            "user": user,
        }
    )

    return build_response(
        201, {"message": f"News cerated with id `{news_id.split('#')[-1]}`"}
    )
