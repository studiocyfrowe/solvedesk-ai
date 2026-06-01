from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from api.auth.jwt_provider import JwtProvider
from infrastructure.dependencies import get_embedder, get_vector_store, get_external_api_source

from dotenv import load_dotenv
import os

load_dotenv()

_data_sync_service = None

security = HTTPBearer(auto_error=False)

JWT_SECRET = os.getenv("JWT_SECRET")
ISSUES_URL = os.getenv("ISSUES_URL")

AUTH_ENABLED = os.getenv(
    "AUTH_ENABLED",
    "false"
).lower() == "true"

jwt_provider = JwtProvider(
    secret=JWT_SECRET
)

def get_current_token(
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    if not AUTH_ENABLED:
        return None
    
    if not credentials:
        raise HTTPException(
            status_code=401,
            detail="Brak tokena"
        )

    if credentials.scheme.lower() != "bearer":
        raise HTTPException(
            status_code=401,
            detail="Niepoprawny schemat tokena"
        )

    token = credentials.credentials

    if not token:
        raise HTTPException(
            status_code=401,
            detail="Pusty token"
        )

    return token

def get_data_sync_service(
    token: str = Depends(get_current_token)
):
    global _data_sync_service
    if AUTH_ENABLED and not token:
        raise HTTPException(
            status_code=403,
            detail="Brak uwierzytelnienia do API"
        )

    source = get_external_api_source(token=token)
    embedder = get_embedder()
    
    if _data_sync_service is None:
        _data_sync_service = get_data_sync_service(
            source, 
            embedder, 
            get_vector_store())
        
    return _data_sync_service