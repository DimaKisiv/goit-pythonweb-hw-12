"""
Password hashing and verification utilities.

Provides functions to hash and verify passwords using bcrypt.
"""
import bcrypt


def get_password_hash(password: str) -> str:
    """
    Hash a password using bcrypt.

    :param password: Plain text password.
    :type password: str
    :return: Hashed password.
    :rtype: str
    """
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
    return hashed_password.decode('utf-8')


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify a plain password against a hashed password.

    :param plain_password: Plain text password.
    :type plain_password: str
    :param hashed_password: Hashed password.
    :type hashed_password: str
    :return: True if password matches, False otherwise.
    :rtype: bool
    """
    return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))
