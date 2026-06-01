from fastapi import HTTPException
import jwt
from domain.ports.auth_provider import AuthProvider
from domain.errors.auth_error import AuthError

class JwtProvider(AuthProvider):
    def __init__(self, secret: str):
        self.secret = secret

    def verify(self, token: str) -> dict:
        try:
            payload = jwt.decode(token, self.secret, algorithms=["HS256"])
            if not payload:
                raise AuthError()
            return payload
        except Exception:
            raise AuthError()