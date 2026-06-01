from fastapi import Request
from fastapi.responses import JSONResponse
from domain.errors.auth_error import AuthError

def register_auth_handlers(app):
    @app.exception_handler(AuthError)
    async def auth_error_handler(request: Request, exc):
        return JSONResponse(status_code=401, content={ "detail" : "Niepoprawny token"})