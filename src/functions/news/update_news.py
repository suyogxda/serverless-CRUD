import json

from src.utils.decorators import error_handler, auth_handler
from src.utils.utils import build_response, generate_expression_and_values


@error_handler
@auth_handler
def api(event, context):
    table = event.get("dynamodb-table")
    path_params = (
        event.get("pathParameters") if event.get("pathParameters") else {}
    )
    body = json.loads(event["body"]) if event.get("body") else {}

    # Send 400 if id is not provided in params
    if not path_params.get("id"):
        return build_response(
            400,
            {"message": "News id must be provided in url as path parameter"},
        )

    # Dynamically generate query expression
    update_expression, expression_attr_values = generate_expression_and_values(
        body
    )

    # Update only if news exists else, send 404
    news = table.update_item(
        Key={"pk": f"NEWS#{path_params.get('id')}", "sk": "NEWS"},
        ReturnValues="ALL_NEW",
        ConditionExpression="attribute_exists(pk)",
        UpdateExpression=update_expression,
        ExpressionAttributeValues=expression_attr_values,
    )

    return build_response(200, news.get("Attributes"))
