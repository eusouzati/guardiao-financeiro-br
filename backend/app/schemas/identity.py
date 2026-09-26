from __future__ import annotations

from uuid import UUID

from app.schemas.common import ApiModel


class OrganizationResponse(ApiModel):
    id: UUID
    legal_name: str
    tax_id: str | None


class MeResponse(ApiModel):
    user_id: str
    display_name: str
    auth_method: str
    roles: list[str]
    permissions: list[str]
    organization: OrganizationResponse
