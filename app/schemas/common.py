"""通用 Schema：分页信封（教程第 07 章 2.3 节）。

泛型 Page[T] 让不同接口复用同一个分页结构：
    response_model=Page[TeamCard]
    response_model=Page[RecruitmentOut]
Pydantic v2 支持 BaseModel + Generic[T] 这种写法。
"""
from typing import Generic, TypeVar

from pydantic import BaseModel, Field

T = TypeVar("T")


class Page(BaseModel, Generic[T]):
    items: list[T]
    total: int = Field(ge=0, description="满足条件的总条数")
    skip: int = Field(ge=0)
    limit: int = Field(ge=1)


class MessageResponse(BaseModel):
    """不做数据包装时，至少给个统一小响应。"""
    message: str
