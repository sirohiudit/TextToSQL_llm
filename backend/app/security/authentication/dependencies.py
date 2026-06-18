from fastapi import Header, HTTPException

from .auth import decode_token

def get_current_user(
    authorization: str = Header(None)
):

    if not authorization:
        raise HTTPException(
            status_code=401,
            detail="Missing token"
        )

    try:

        token = authorization.replace(
            "Bearer ",
            ""
        )

        payload = decode_token(token)

        return int(payload["sub"])

    except Exception:

        raise HTTPException(
            status_code=401,
            detail="Invalid token"
        )