import hashlib
import hmac
import secrets


_PASSWORD_ITERATIONS = 600_000
_HASH_ALGORITHM = "sha256"
_HASH_SCHEME = "pbkdf2_sha256"


def hash_password(password: str) -> str:
    salt = secrets.token_bytes(16)
    derived_key = hashlib.pbkdf2_hmac(
        _HASH_ALGORITHM,
        password.encode("utf-8"),
        salt,
        _PASSWORD_ITERATIONS,
    )
    return f"{_HASH_SCHEME}${_PASSWORD_ITERATIONS}${salt.hex()}${derived_key.hex()}"


def verify_password(password: str, password_hash: str) -> bool:
    try:
        scheme, iterations_text, salt_hex, expected_hex = password_hash.split("$")
        iterations = int(iterations_text)
        salt = bytes.fromhex(salt_hex)
        expected = bytes.fromhex(expected_hex)
    except (AttributeError, TypeError, ValueError):
        return False

    if scheme != _HASH_SCHEME or iterations < 1 or not salt or not expected:
        return False

    actual = hashlib.pbkdf2_hmac(
        _HASH_ALGORITHM, password.encode("utf-8"), salt, iterations
    )
    return hmac.compare_digest(actual, expected)
