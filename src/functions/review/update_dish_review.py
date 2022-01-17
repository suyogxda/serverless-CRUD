import json

from src.utils.decorators import error_handler, auth_handler
from src.utils.utils import build_response, generate_expression_and_values
from src.validators.review_validator import UpdateReview


@error_handler
@auth_handler
def api(event, context):
    table = event.get("dynamodb-table")
    user = event.get("auth-user")
    path_params = (
        event.get("pathParameters") if event.get("pathParameters") else {}
    )
    body = json.loads(event["body"]) if event.get("body") else {}

    # Send 400 if id is not provided in params
    if not path_params.get("id"):
        return build_response(
            400,
            {"message": "Review id must be provided in url as path parameter"},
        )

    # Validate fields
    UpdateReview(**body)

    # Dynamically generate query expression
    update_expression, expression_attr_values = generate_expression_and_values(
        body
    )

    # Update only if review exists else, send 404
    _review = table.query(
        IndexName="sk-meta1-index",
        Limit=1,
        KeyConditionExpression="#meta1 = :meta1 and #sk = :sk",
        ExpressionAttributeNames={"#meta1": "meta1", "#sk": "sk"},
        ExpressionAttributeValues={
            ":meta1": f"DISH#{path_params.get('id')}",
            ":sk": f"REVIEW#DISH#{user}",
        },
    ).get("Items")
    if not _review:
        return build_response(404, {"message": "Not found"})
    review = table.update_item(
        Key={
            "pk": _review[0].get("pk"),
            "sk": f"REVIEW#DISH#{user}",
        },
        ReturnValues="ALL_NEW",
        ConditionExpression="attribute_exists(pk)",
        UpdateExpression=update_expression,
        ExpressionAttributeValues=expression_attr_values,
    )

    return build_response(200, review.get("Attributes"))
