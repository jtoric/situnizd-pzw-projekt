from fastapi import Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException


class AppError(Exception):
    """Domenska pogreška: sloj services je podiže, handler je prevodi u odgovor.

    code je stalan i namijenjen kodu klijenta, message čovjeku.
    """

    def __init__(self, code: str, message: str, status_code: int = 400):
        self.code = code
        self.message = message
        self.status_code = status_code


async def app_error_handler(_request: Request, exc: AppError) -> JSONResponse:
    return JSONResponse(
        status_code=exc.status_code,
        content={"code": exc.code, "message": exc.message},
    )


async def validation_error_handler(
    _request: Request, exc: RequestValidationError
) -> JSONResponse:
    # Isti oblik kao AppError, uz popis polja koja nisu prošla provjeru
    errors = []
    for err in exc.errors():
        loc = [str(part) for part in err["loc"] if part != "body"]
        message = err["msg"].removeprefix("Value error, ")
        errors.append({"field": ".".join(loc), "message": message})
    return JSONResponse(
        status_code=422,
        content={
            "code": "validation_error",
            "message": "Neispravni podatci u zahtjevu",
            "errors": errors,
        },
    )


HTTP_ERROR_CODES = {404: "not_found", 405: "method_not_allowed"}


async def http_exception_handler(
    _request: Request, exc: StarletteHTTPException
) -> JSONResponse:
    # Pogreške koje podiže sam framework, npr. nepostojeća putanja
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "code": HTTP_ERROR_CODES.get(exc.status_code, "http_error"),
            "message": str(exc.detail),
        },
        headers=getattr(exc, "headers", None),
    )
