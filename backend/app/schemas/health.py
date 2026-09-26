from __future__ import annotations

from typing import Literal

from app.schemas.common import ApiModel


class LivenessResponse(ApiModel):
    status: Literal["ok"]


class ReadinessResponse(ApiModel):
    status: Literal["ok", "unavailable"]
    version: str
    environment: str
    database: Literal["ok", "unavailable"]
    schema_revision: str | None
