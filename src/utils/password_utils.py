import hashlib
import os
from base64 import b64decode


def hash_password(password):
    salt = os.urandom(32)
    key = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, 10000)
    return key + salt


def verify_password(password, hashed_password, decode=False):
    hashed_password = b64decode(hashed_password) if decode else hashed_password
    key, salt = hashed_password[:32], hashed_password[32:]
    return key == hashlib.pbkdf2_hmac(
        "sha256", password.encode("utf-8"), salt, 10000
    )
