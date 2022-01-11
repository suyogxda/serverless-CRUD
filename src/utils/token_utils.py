import json
import os
import hashlib
from datetime import datetime


def make_token(email):
    salt = os.urandom(32)
    payload = {"email": email, "expires_in": datetime.utcnow()}
    _payload = json.stringify(payload)
    key = hashlib.pbkdf2_hmac("sha256", _payload.encode("utf-8"), salt, 10000)
    return key + salt
