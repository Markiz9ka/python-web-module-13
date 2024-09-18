import fastapi
import fastapi.responses

class AuthException(Exception):
    pass


def auth_error_handler(request, exc):
    return fastapi.responses.JSONResponse(
        status_code=fastapi.status.HTTP_401_UNAUTHORIZED,
        headers={
            "WWW-Authenticate": "Bearer"
        },
        content={
            "details": str(exc),
        }
    )
