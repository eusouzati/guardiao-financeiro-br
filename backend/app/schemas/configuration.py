from __future__ import annotations

from datetime import datetime

from pydantic import Field

from app.schemas.common import ApiModel

# Decimais trafegam como string (ADR-007); booleanos e inteiros como tipos JSON nativos.
type JsonPolicyValue = bool | int | str


class PolicyResponse(ApiModel):
    key: str
    label: str
    description: str
    type: str = Field(examples=["BOOLEAN", "INTEGER", "DECIMAL", "SEVERITY"])
    unit: str | None
    value: JsonPolicyValue
    default_value: JsonPolicyValue
    allowed_values: list[str]
    minimum: str | None
    maximum: str | None
    source: str = Field(examples=["DEFAULT", "ORGANIZATION"])
    version: int | None
    changed_by: str | None
    changed_at: datetime | None


class ConfigurationResponse(ApiModel):
    items: list[PolicyResponse]
