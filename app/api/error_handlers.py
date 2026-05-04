from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from starlette import status

from app.core.exceptions import (
    EmailAlreadyExistsError,
    InvalidCredentialsError,
    NotFoundError,
    UserSuspendedError,
)


def register_exception_handlers(app: FastAPI) -> None:
    @app.exception_handler(NotFoundError)
    def not_found_handler(request: Request, exception: NotFoundError) -> JSONResponse:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND, content={"detail": str(exception)}
        )

    @app.exception_handler(EmailAlreadyExistsError)
    def email_exists_handler(request: Request, exception: EmailAlreadyExistsError) -> JSONResponse:
        return JSONResponse(
            status_code=status.HTTP_409_CONFLICT, content={"detail": str(exception)}
        )

    @app.exception_handler(InvalidCredentialsError)
    def invalid_credentials_handler(
        request: Request, exception: InvalidCredentialsError
    ) -> JSONResponse:
        return JSONResponse(
            status_code=status.HTTP_401_UNAUTHORIZED, content={"detail": str(exception)}
        )

    @app.exception_handler(UserSuspendedError)
    def suspended_handler(request: Request, exception: UserSuspendedError) -> JSONResponse:
        return JSONResponse(
            status_code=status.HTTP_403_FORBIDDEN, content={"detail": str(exception)}
        )
