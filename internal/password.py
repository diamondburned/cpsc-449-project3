# Code taken and slightly modified from
# https://til.simonwillison.net/python/password-hashing-with-pbkdf2.
# All credit goes to Simon Willison.

import base64
import hashlib
import secrets


ALGORITHM = "pbkdf2_sha256"


def hash_password(password: str, salt: str | None = None, iterations=260000):
    if salt is None:
        salt = secrets.token_hex(16)
    assert "$" not in salt

    pw_hash = hashlib.pbkdf2_hmac(
        "sha256",
        password.encode("utf-8"),
        salt.encode("utf-8"),
        iterations,
    )
    b64_hash = base64.b64encode(pw_hash).decode("ascii").strip()
    return "{}${}${}${}".format(ALGORITHM, iterations, salt, b64_hash)


def verify_password(password: str, password_hash: str):
    if (password_hash or "").count("$") != 3:
        return False

    algorithm, iterations, salt, b64_hash = password_hash.split("$", 3)
    iterations = int(iterations)
    assert algorithm == ALGORITHM

    compare_hash = hash_password(password, salt, iterations)
    return secrets.compare_digest(password_hash, compare_hash)
