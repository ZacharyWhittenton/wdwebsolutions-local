import os
import secrets
import time

import boto3
from fastapi import Cookie, Depends, HTTPException, status
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

USERS_TABLE = os.environ.get("USERS_TABLE", "wdweb-users")
SESSIONS_TABLE = os.environ.get("SESSIONS_TABLE", "wdweb-sessions")
SESSION_TTL_SECONDS = 60 * 60 * 24 * 7  # 7 days

_dynamodb = None


def get_dynamodb():
    global _dynamodb
    if _dynamodb is None:
        _dynamodb = boto3.resource("dynamodb", region_name=os.environ.get("AWS_REGION", "us-east-1"))
    return _dynamodb


def users_table():
    return get_dynamodb().Table(USERS_TABLE)


def sessions_table():
    return get_dynamodb().Table(SESSIONS_TABLE)


class AuthError(Exception):
    pass


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(password: str, password_hash: str) -> bool:
    return pwd_context.verify(password, password_hash)


def create_user(email: str, password: str, role: str = "user") -> dict:
    existing = users_table().get_item(Key={"email": email}).get("Item")
    if existing:
        raise AuthError("An account with this email already exists")

    user = {"email": email, "password_hash": hash_password(password), "role": role}
    users_table().put_item(Item=user)
    return {"email": email, "role": role}


def authenticate_user(email: str, password: str) -> dict:
    user = users_table().get_item(Key={"email": email}).get("Item")
    if not user or not verify_password(password, user["password_hash"]):
        raise AuthError("Invalid email or password")
    return {"email": user["email"], "role": user["role"]}


def create_session(email: str) -> str:
    session_id = secrets.token_urlsafe(32)
    sessions_table().put_item(Item={
        "session_id": session_id,
        "email": email,
        "expires_at": int(time.time()) + SESSION_TTL_SECONDS,
    })
    return session_id


def destroy_session(session_id: str) -> None:
    sessions_table().delete_item(Key={"session_id": session_id})


def get_current_user(session_id: str | None = Cookie(default=None)) -> dict:
    if not session_id:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Not authenticated")

    session = sessions_table().get_item(Key={"session_id": session_id}).get("Item")
    if not session or session["expires_at"] < int(time.time()):
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Session expired")

    user = users_table().get_item(Key={"email": session["email"]}).get("Item")
    if not user:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "User not found")

    return {"email": user["email"], "role": user["role"]}


def require_role(role: str):
    def checker(user: dict = Depends(get_current_user)) -> dict:
        if user["role"] != role:
            raise HTTPException(status.HTTP_403_FORBIDDEN, "Insufficient permissions")
        return user
    return checker
