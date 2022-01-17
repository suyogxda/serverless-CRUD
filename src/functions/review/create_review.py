import json
import uuid
from datetime import datetime, timezone


from src.utils.decorators import error_handler, auth_handler
from src.utils.utils import build_response
from src.validators.review_validator import CreateReview


"""
DATA MODEL:
    {
        pk: f'REVIEW#{review_id}': str,
        sk: AnyOf[f'REVIEW#DISH#USER#{user_id}', f'REVIEW#RESTAURANT#USER#{user_id}']: str,
        created_at: timestamp: int,
        user: f'USER#{user_id}': str,
        description: 'Some description': str,
        meta1: AnyOf[f'DISH#{dish_id}', f'RESTAURANT#{restaurant_id}']: str,
        stars: AnyOf[1, 2, 3, 4, 5]: int
    }
"""


@error_handler
@auth_handler
def api(event, context):
    table = event.get("dynamodb-table")

    body = json.loads(event["body"])
    user = event.get("auth-user")

    # Validation
    CreateReview(**body)

    # Identify if item type is dish or restaurant
    item_type = body.get("type")
    item_id = (
        f"DISH#{body.get('item_id')}"
        if item_type == "dish"
        else f"RESTAURANT#{body.get('item_id')}"
    )
    sort_key = (
        f"REVIEW#DISH#{user}"
        if item_type == "dish"
        else f"REVIEW#RESTAURANT#{user}"
    )

    # Check if existing review for same dish/restaurant by same user exists
    existing_review = table.query(
        IndexName="sk-meta1-index",
        Limit=1,
        KeyConditionExpression="#meta1 = :meta1 and #sk = :sk",
        ExpressionAttributeNames={"#meta1": "meta1", "#sk": "sk"},
        ExpressionAttributeValues={":meta1": item_id, ":sk": sort_key},
    ).get("Items")
    # Send 400 if review already exists
    if existing_review:
        return build_response(
            400,
            {"message": f"Review for item by user: `{user}` already exists"},
        )

    # Insert into db
    review_id = f"REVIEW#{uuid.uuid4()}"
    table.put_item(
        Item={
            "pk": review_id,
            "sk": sort_key,
            "meta1": item_id,
            "user": user,
            "stars": int(body.get("stars")),
            "description": body.get("description"),
            "created_at": int(datetime.now(timezone.utc).timestamp()),
        }
    )

    return build_response(
        201,
        {"message": f"Review cerated with id `{review_id.split('#')[-1]}`"},
    )
