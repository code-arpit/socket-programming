import uuid

from fastapi import Depends, HTTPException, Request
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from typing import Dict
from jose import jwt
from settings import settings


async def decode_jwt(
    jwt_token: str,
) -> Dict:
    try:
        return jwt.decode(
            jwt_token,
            key=settings.SECRET_KEY,
            algorithms=[settings.JWT_ALGORITHM],
            options={"verify_signature": False},
        )
    except Exception as e:
        raise HTTPException(
            status_code=403,
            detail="Invalid token or expired token.",
        ) from e


class JWTBearer(HTTPBearer):
    def __init__(
        self,
        auto_error: bool = True,
    ):
        super().__init__(auto_error=auto_error)

    async def __call__(
        self,
        request: Request,
    ) -> HTTPAuthorizationCredentials | None:
        credentials = await super().__call__(request)
        if credentials:
            if not credentials.scheme == "Bearer":
                raise HTTPException(
                    status_code=403,
                    detail="Invalid authentication scheme.",
                )
            if not await self.verify_jwt(credentials.credentials):
                raise HTTPException(
                    status_code=403,
                    detail="Invalid token or expired token.",
                )
            return credentials.credentials

        raise HTTPException(
            status_code=403,
            detail="Invalid authorization code.",
        )

    async def verify_jwt(
        self,
        jwt_token: str,
    ) -> bool:
        payload = await decode_jwt(
            jwt_token,
        )

        return bool(payload)

    @staticmethod
    async def get_current_user_id(
        token: str,
    ) -> uuid.UUID:
        decoded = await decode_jwt(token.replace("Bearer ", ""))
        return uuid.UUID(decoded["user_id"])


async def get_current_user(token: str = Depends(JWTBearer())):
    return await JWTBearer.get_current_user_id(
        token=token,
    )
