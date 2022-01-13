import decimal
import json


class DecimalEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, decimal.Decimal):
            return int(o)
        return super(DecimalEncoder, self).default(o)


def build_response(code: int, body):
    """
    Build standard JSON response
    :param code: int: HTTP status code
    :param body: AnyOf [JSON serializable string, dict]: Body to serialize
    :returns: dict[dict, Any] Response JSON
    """
    return {
        "statusCode": code,
        "headers": {"Content-Type": "application/json"},
        "body": json.dumps(body, cls=DecimalEncoder),
        "isBase64Encoded": False,
    }


def generate_expression_and_values(body: dict):
    """
    Helper function to generate UpdateExpression and ExpressionAttributeValues for given dict
    :param body: dict: required: [payload]
    :returns: [UpdateExpression: str, ExpressionAttributeValues: dict] if body has data else [None, None]]
    """
    update_expression = _to_compare = "SET "
    attributes_value = {}
    for key, value in body.items():
        update_expression += f"{key} = :{key}, "
        attributes_value[f":{key}"] = value

    update_expression = (
        update_expression[:-2]
        if update_expression != _to_compare
        else update_expression
    )

    return (
        [update_expression, attributes_value]
        if update_expression != _to_compare
        else [None, None]
    )
