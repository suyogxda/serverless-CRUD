import json


def build_response(code, message):
    return {
        "statusCode": code,
        "headers": {"Content-Type": "application/json"},
        "body": json.dumps({"message": message}),
        "isBase64Encoded": False,
    }
