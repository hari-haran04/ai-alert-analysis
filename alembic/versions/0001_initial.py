"""initial schema

Revision ID: 0001_initial
Revises:
Create Date: 2026-10-07
"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa
from pgvector.sqlalchemy import Vector

revision = "0001_initial"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("CREATE EXTENSION IF NOT EXISTS vector")
    op.create_table(
        "alerts",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("alert_id", sa.String(length=100), nullable=False, unique=True),
        sa.Column("screening_type", sa.String(length=50), nullable=False),
        sa.Column("created_at", sa.DateTime(), server_default=sa.func.now()),
    )
    op.create_index("ix_alerts_alert_id", "alerts", ["alert_id"])
    op.create_table(
        "historical_cases",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("case_id", sa.String(length=100), nullable=False, unique=True),
        sa.Column("alert_id", sa.String(length=100), nullable=False),
        sa.Column("classification", sa.String(length=50), nullable=False),
        sa.Column("analyst_decision", sa.String(length=50), nullable=False),
        sa.Column("summary", sa.Text(), nullable=False),
        sa.Column("attributes", sa.JSON(), nullable=False),
        sa.Column("reasoning", sa.JSON(), nullable=False),
        sa.Column("embedding", Vector(1024), nullable=True),
        sa.Column("created_at", sa.DateTime(), server_default=sa.func.now()),
    )
    op.create_index("ix_historical_cases_case_id", "historical_cases", ["case_id"])
    op.execute(
        "CREATE INDEX IF NOT EXISTS ix_historical_cases_embedding "
        "ON historical_cases USING ivfflat (embedding vector_cosine_ops) WITH (lists = 100)"
    )
    op.create_table(
        "third_parties",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("alert_id", sa.Integer(), sa.ForeignKey("alerts.id"), nullable=False),
        sa.Column("entity_id", sa.String(length=100)),
        sa.Column("name", sa.Text(), nullable=False),
        sa.Column("country", sa.String(length=100)),
        sa.Column("city", sa.String(length=100)),
        sa.Column("date_of_birth", sa.String(length=40)),
        sa.Column("passport_number_hash", sa.String(length=128)),
        sa.Column("registration_number_hash", sa.String(length=128)),
        sa.Column("tax_id_hash", sa.String(length=128)),
        sa.Column("address", sa.Text()),
    )
    op.create_table(
        "hits",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("alert_id", sa.Integer(), sa.ForeignKey("alerts.id"), nullable=False),
        sa.Column("hit_id", sa.String(length=100), nullable=False),
        sa.Column("name", sa.Text(), nullable=False),
        sa.Column("country", sa.String(length=100)),
        sa.Column("city", sa.String(length=100)),
        sa.Column("date_of_birth", sa.String(length=40)),
        sa.Column("passport_number_hash", sa.String(length=128)),
        sa.Column("registration_number_hash", sa.String(length=128)),
        sa.Column("tax_id_hash", sa.String(length=128)),
        sa.Column("address", sa.Text()),
        sa.Column("score", sa.Float()),
        sa.Column("level", sa.String(length=50)),
        sa.Column("list_type", sa.String(length=100)),
        sa.Column("source", sa.String(length=100)),
    )
    op.create_table(
        "analyses",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("alert_id_fk", sa.Integer(), sa.ForeignKey("alerts.id")),
        sa.Column("alert_id", sa.String(length=100), nullable=False),
        sa.Column("classification", sa.String(length=50), nullable=False),
        sa.Column("confidence", sa.Float(), nullable=False),
        sa.Column("risk_level", sa.String(length=50), nullable=False),
        sa.Column("model_version", sa.String(length=50), nullable=False),
        sa.Column("rule_version", sa.String(length=50), nullable=False),
        sa.Column("llm_model", sa.String(length=100)),
        sa.Column("input_hash", sa.String(length=128), nullable=False),
        sa.Column("model_prediction", sa.JSON(), nullable=False),
        sa.Column("rule_results", sa.JSON(), nullable=False),
        sa.Column("historical_cases_used", sa.JSON(), nullable=False),
        sa.Column("final_recommendation", sa.JSON(), nullable=False),
        sa.Column("created_at", sa.DateTime(), server_default=sa.func.now()),
    )
    op.create_table(
        "attribute_analyses",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("analysis_id", sa.Integer(), sa.ForeignKey("analyses.id"), nullable=False),
        sa.Column("hit_id", sa.String(length=100), nullable=False),
        sa.Column("attribute_name", sa.String(length=100), nullable=False),
        sa.Column("result", sa.String(length=50), nullable=False),
        sa.Column("similarity", sa.Float()),
        sa.Column("weight", sa.Float(), nullable=False),
        sa.Column("evidence", sa.String(length=500), nullable=False),
    )
    op.create_table(
        "analyst_feedback",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("alert_id", sa.String(length=100), nullable=False),
        sa.Column("ai_classification", sa.String(length=50), nullable=False),
        sa.Column("analyst_classification", sa.String(length=50), nullable=False),
        sa.Column("analyst_comment", sa.Text()),
        sa.Column("created_at", sa.DateTime(), server_default=sa.func.now()),
    )
    op.create_table(
        "model_versions",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("model_name", sa.String(length=100), nullable=False),
        sa.Column("model_version", sa.String(length=50), nullable=False),
        sa.Column("training_dataset_version", sa.String(length=50), nullable=False),
        sa.Column("features", sa.JSON(), nullable=False),
        sa.Column("metrics", sa.JSON(), nullable=False),
        sa.Column("trained_at", sa.DateTime(), server_default=sa.func.now()),
    )
    op.create_table(
        "rule_versions",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("version", sa.String(length=50), nullable=False, unique=True),
        sa.Column("config", sa.JSON(), nullable=False),
        sa.Column("created_at", sa.DateTime(), server_default=sa.func.now()),
    )
    op.create_table(
        "audit_logs",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("alert_id", sa.String(length=100), nullable=False),
        sa.Column("input_hash", sa.String(length=128), nullable=False),
        sa.Column("model_version", sa.String(length=50), nullable=False),
        sa.Column("rule_version", sa.String(length=50), nullable=False),
        sa.Column("llm_model", sa.String(length=100)),
        sa.Column("event", sa.String(length=100), nullable=False),
        sa.Column("payload", sa.JSON(), nullable=False),
        sa.Column("created_at", sa.DateTime(), server_default=sa.func.now()),
    )


def downgrade() -> None:
    for table in [
        "audit_logs",
        "rule_versions",
        "model_versions",
        "analyst_feedback",
        "attribute_analyses",
        "analyses",
        "hits",
        "third_parties",
        "historical_cases",
        "alerts",
    ]:
        op.drop_table(table)
