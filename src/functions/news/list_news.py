from src.errors.generic_error import GenericError
from src.utils.decorators import error_handler, auth_handler
from src.utils.utils import build_response


@error_handler
@auth_handler
def api(event, context):
    table = event.get("dynamodb-table")
    args = event.get("arguments") if event.get("arguments") else {}
    limit = args.get("limit") if args.get("limit") else 10
    try:
        limit = int(limit)
    except (ValueError, TypeError):
        raise GenericError("Limit must be an integer")
    news = table.query(
        IndexName="filter",
        Limit=limit,
        KeyConditionExpression="#sk = :sk and begins_with(#pk, :pk)",
        ExpressionAttributeNames={"#sk": "sk", "#pk": "pk"},
        ExpressionAttributeValues={":sk": "NEWS", ":pk": "NEWS"},
    ).get("Items")

    # Send just id of news and user in response
    [
        (
            x.update({"user": x["user"].split("#")[-1]}),
            x.update({"pk": x["pk"].split("#")[-1]}),
        )
        for x in news
    ]

    return build_response(200, news)
