from src.errors.generic_error import GenericError
from src.utils.decorators import error_handler, auth_handler
from src.utils.utils import build_response


@error_handler
@auth_handler
def api(event, context):
    table = event.get("dynamodb-table")
    args = event.get("arguments") if event.get("arguments") else {}
    limit = args.get("limit") if args.get("limit") else 10

    path_params = (
        event.get("pathParameters") if event.get("pathParameters") else {}
    )
    if not path_params.get("id"):
        return build_response(
            400,
            {
                "message": "Restaurant id must be provided in url as path parameter"
            },
        )

    try:
        limit = int(limit)
    except (ValueError, TypeError):
        raise GenericError("Limit must be an integer")
    reviews = table.query(
        IndexName="meta1-pk-index",
        Limit=limit,
        KeyConditionExpression="begins_with(#pk, :pk) and #meta1 = :meta1",
        ExpressionAttributeNames={"#pk": "pk", "#meta1": "meta1"},
        ExpressionAttributeValues={
            ":pk": "REVIEW#",
            ":meta1": f"RESTAURANT#{path_params.get('id')}",
        },
    ).get("Items")

    # Send just id of reviews and user in response
    [
        (
            review.update({"user": review["user"].split("#")[-1]}),
            review.update({"meta1": review["meta1"].split("#")[-1]}),
            review.update({"pk": review["pk"].split("#")[-1]}),
        )
        for review in reviews
    ]

    return build_response(200, reviews)
