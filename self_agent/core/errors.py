# 自定义异常与全局错误处理
from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse
from fastapi import status

class APIException(Exception):
    def __init__(self, code: int, message: str, details=None):
        self.code = code
        self.message = message
        self.details = details

def register_exception_handlers(app):
    @app.exception_handler(APIException)
    async def api_exception_handler(request: Request, exc: APIException):
        return JSONResponse(
            status_code=exc.code // 1000,
            content={
                "code": exc.code,
                "message": exc.message,
                "details": exc.details,
            },
        )

    @app.exception_handler(HTTPException)
    async def http_exception_handler(request: Request, exc: HTTPException):
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "code": exc.status_code * 10,
                "message": exc.detail,
                "details": None,
            },
        )

    @app.exception_handler(Exception)
    async def generic_exception_handler(request: Request, exc: Exception):
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "code": 5000,
                "message": "Internal server error",
                "details": str(exc),
            },
        )
