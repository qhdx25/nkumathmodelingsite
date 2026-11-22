"""统一异常与响应格式（教程第 02 章、第 08 章）。

目标：所有「失败」响应都长成同一种结构
    {"code": 400xx, "message": "人类可读原因", "data": 详情或 null}

成功响应则由各路由的 response_model 直接描述数据本身（不套外壳），
这样 /docs 文档就是真实返回结构，前端也能直接拿到数据。

FastAPI 的异常处理器是「全局挂载」的：
    @app.exception_handler(异常类) → 注册一个函数，任何路由抛出该类异常都会被它接管。
"""
from typing import Any

from fastapi import FastAPI, Request, status
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException


class BusinessError(Exception):
    """业务异常：由服务层抛出，表达「参数合法但业务规则不允许」。

    例如重复申请、队伍已满、状态流转非法。HTTP 状态码默认 400，
    具体的业务错误码由 code 字段携带，便于前端精确处理。
    """

    def __init__(self, message: str, code: int = 40000, http_status: int = 400):
        self.message = message
        self.code = code
        self.http_status = http_status
        super().__init__(message)


def ok(data: Any = None, message: str = "ok") -> dict:
    """成功响应的统一包装（在路由里 return ok(data) 即可）。"""
    return {"code": 0, "message": message, "data": data}


async def business_error_handler(request: Request, exc: BusinessError) -> JSONResponse:
    return JSONResponse(
        status_code=exc.http_status,
        content={"code": exc.code, "message": exc.message, "data": None},
    )


async def validation_error_handler(
    request: Request, exc: RequestValidationError
) -> JSONResponse:
    """把 Pydantic 的 422 细节挪到 data 字段，外层结构保持一致。

    jsonable_encoder 是必需的：exc.errors() 的 ctx 里可能含 ValueError 对象，
    直接塞进 JSONResponse 会序列化失败。
    """
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "code": 42200,
            "message": "参数校验失败",
            "data": jsonable_encoder(exc.errors()),
        },
    )


async def http_error_handler(
    request: Request, exc: StarletteHTTPException
) -> JSONResponse:
    """把 HTTPException（401/403/404 等）也包成统一格式。"""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "code": exc.status_code * 100,
            "message": str(exc.detail),
            "data": None,
        },
        headers=getattr(exc, "headers", None),
    )


def register_exception_handlers(app: FastAPI) -> None:
    """在 main.py 里一次性挂载所有全局异常处理器。"""
    app.add_exception_handler(BusinessError, business_error_handler)
    app.add_exception_handler(RequestValidationError, validation_error_handler)
    app.add_exception_handler(StarletteHTTPException, http_error_handler)
