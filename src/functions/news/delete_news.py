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

    # Update only if news exists else, send 404
    table.delete_item(
        Key={"pk": f"NEWS#{path_params.get('id')}", "sk": "NEWS"},
        ReturnValues="ALL_OLD",
        ConditionExpression="attribute_exists(pk)",
    )

    return build_response(
        200, {"message": f"News with id `{path_params.get('id')}` deleted"}
    )
