from __future__ import annotations

from datetime import datetime
from typing import Any
from uuid import UUID

from app.schemas.common import ApiModel, PageMeta


class AuditEventResponse(ApiModel):
    id: UUID
    occurred_at: datetime
    event_type: str
    actor_type: str
    actor_id: str
    request_id: str | None
    target_type: str | None
    target_id: str | None
    details: dict[str, Any]


class AuditEventPage(ApiModel):
    items: list[AuditEventResponse]
    meta: PageMeta
