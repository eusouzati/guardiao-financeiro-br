"""Schema inicial: organization, configuration (versionada) e audit_event (append-only).

Revision ID: 0001
Revises:
Create Date: 2026-09-26
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "0001"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

# Lista fixa nesta revisão: novos tipos de evento exigem nova migration (histórico explícito).
EVENT_TYPES = (
    "DOCUMENT_UPLOADED",
    "DOCUMENT_PARSED",
    "DOCUMENT_MATCHED",
    "EXCEPTION_CREATED",
    "EXCEPTION_RESOLVED",
    "DOCUMENT_REVIEWED",
    "CONFIGURATION_CHANGED",
    "IMPORT_STARTED",
    "IMPORT_COMPLETED",
    "LOGIN_SUCCESS",
    "LOGIN_FAILURE",
    "ORGANIZATION_CREATED",
)

APPEND_ONLY_FUNCTION = """
CREATE FUNCTION gfb_reject_mutation() RETURNS trigger
LANGUAGE plpgsql AS $$
BEGIN
    RAISE EXCEPTION 'A tabela % é append-only: % não é permitido.', TG_TABLE_NAME, TG_OP
        USING ERRCODE = 'restrict_violation';
END;
$$;
"""

APPEND_ONLY_TABLES = ("audit_event", "configuration")


def upgrade() -> None:
    op.create_table(
        "organization",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("legal_name", sa.String(length=200), nullable=False),
        sa.Column("tax_id", sa.String(length=14), nullable=True),
        sa.Column("status", sa.String(length=20), server_default="ACTIVE", nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.CheckConstraint(
            "status IN ('ACTIVE', 'INACTIVE')", name=op.f("ck_organization_status_valid")
        ),
        sa.CheckConstraint(
            "tax_id IS NULL OR tax_id ~ '^[0-9A-Z]{12}[0-9]{2}$'",
            name=op.f("ck_organization_tax_id_format"),
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_organization")),
        sa.UniqueConstraint("tax_id", name=op.f("uq_organization_tax_id")),
    )

    op.create_table(
        "configuration",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("organization_id", sa.Uuid(), nullable=False),
        sa.Column("key", sa.String(length=100), nullable=False),
        sa.Column("value", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("version", sa.Integer(), nullable=False),
        sa.Column("changed_by", sa.String(length=200), nullable=False),
        sa.Column(
            "changed_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.CheckConstraint("version >= 1", name=op.f("ck_configuration_version_positive")),
        sa.ForeignKeyConstraint(
            ["organization_id"],
            ["organization.id"],
            name=op.f("fk_configuration_organization_id_organization"),
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_configuration")),
        sa.UniqueConstraint(
            "organization_id",
            "key",
            "version",
            name=op.f("uq_configuration_organization_id_key_version"),
        ),
    )

    event_types = ", ".join(f"'{e}'" for e in EVENT_TYPES)
    op.create_table(
        "audit_event",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("organization_id", sa.Uuid(), nullable=False),
        sa.Column(
            "occurred_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column("event_type", sa.String(length=50), nullable=False),
        sa.Column("actor_type", sa.String(length=20), nullable=False),
        sa.Column("actor_id", sa.String(length=200), nullable=False),
        sa.Column("request_id", sa.String(length=64), nullable=True),
        sa.Column("target_type", sa.String(length=50), nullable=True),
        sa.Column("target_id", sa.String(length=100), nullable=True),
        sa.Column(
            "details",
            postgresql.JSONB(astext_type=sa.Text()),
            server_default=sa.text("'{}'::jsonb"),
            nullable=False,
        ),
        sa.CheckConstraint(
            "actor_type IN ('USER', 'SYSTEM')", name=op.f("ck_audit_event_actor_type_valid")
        ),
        sa.CheckConstraint(
            f"event_type IN ({event_types})", name=op.f("ck_audit_event_event_type_valid")
        ),
        sa.ForeignKeyConstraint(
            ["organization_id"],
            ["organization.id"],
            name=op.f("fk_audit_event_organization_id_organization"),
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_audit_event")),
    )
    op.create_index(
        "ix_audit_event_org_occurred_at", "audit_event", ["organization_id", "occurred_at"]
    )

    # Append-only (ADR-015): bloqueia UPDATE/DELETE por linha e TRUNCATE por comando.
    op.execute(APPEND_ONLY_FUNCTION)
    for table in APPEND_ONLY_TABLES:
        op.execute(
            f"CREATE TRIGGER trg_{table}_no_update_delete BEFORE UPDATE OR DELETE ON {table} "
            "FOR EACH ROW EXECUTE FUNCTION gfb_reject_mutation()"
        )
        op.execute(
            f"CREATE TRIGGER trg_{table}_no_truncate BEFORE TRUNCATE ON {table} "
            "FOR EACH STATEMENT EXECUTE FUNCTION gfb_reject_mutation()"
        )


def downgrade() -> None:
    for table in APPEND_ONLY_TABLES:
        op.execute(f"DROP TRIGGER IF EXISTS trg_{table}_no_truncate ON {table}")
        op.execute(f"DROP TRIGGER IF EXISTS trg_{table}_no_update_delete ON {table}")
    op.execute("DROP FUNCTION IF EXISTS gfb_reject_mutation()")
    op.drop_index("ix_audit_event_org_occurred_at", table_name="audit_event")
    op.drop_table("audit_event")
    op.drop_table("configuration")
    op.drop_table("organization")
