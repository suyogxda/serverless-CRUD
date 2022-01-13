from src.utils.decorators import error_handler, auth_handler
from src.utils.utils import build_response


@error_handler
@auth_handler
def api(event, context):
    table = event.get("dynamodb-table")
    path_params = (
        event.get("pathParameters") if event.get("pathParameters") else {}
    )
    if not path_params.get("id"):
        return build_response(
            400,
            {"message": "News id must be provided in url as path parameter"},
        )
    news = table.get_item(
        Key={"pk": f"NEWS#{path_params.get('id')}", "sk": "NEWS"}
    ).get("Item")

    return (
        build_response(200, news)
        if news
        else build_response(
            404,
            {"message": f"News with id `{path_params.get('id')}` not found"},
        )
    )
