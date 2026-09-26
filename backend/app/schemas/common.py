from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field


class ApiModel(BaseModel):
    model_config = ConfigDict(frozen=True)


class ErrorDetail(ApiModel):
    field: str | None = Field(default=None, description="Campo relacionado ao erro, se houver.")
    message: str


class ErrorResponse(ApiModel):
    code: str = Field(examples=["GFB-0403"])
    message: str = Field(examples=["Você não tem permissão para executar esta operação."])
    request_id: str | None = None
    details: list[ErrorDetail] = Field(default_factory=list)


class PageMeta(ApiModel):
    page: int
    page_size: int
    total: int
