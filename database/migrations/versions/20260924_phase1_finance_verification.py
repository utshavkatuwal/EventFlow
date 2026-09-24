"""Phase 1 finance + verification tables.

Revision ID: 20260924_phase1
Revises: 000000000000
Create Date: 2026-09-24

Covers models added after the initial migration:
- finance: payments, wallets, wallet_transactions, withdrawal_requests, platform_settings
- verification: organizer_applications, organizer_documents
- columns: users.account_type, events.video_url,
  organizer_profiles.verification_status/verification_info/rejection_reason

Matches backend/app/models/finance.py + verification.py.
`ensure_phase1_schema()` in app/database keeps older dev DBs working;
this migration is the canonical Alembic path for fresh/prod DBs.
"""
from alembic import op
import sqlalchemy as sa

revision = "20260924_phase1"
down_revision = "000000000000"
branch_labels = None
depends_on = None


def _add_column_if_missing(table: str, column: sa.Column) -> None:
    bind = op.get_bind()
    insp = sa.inspect(bind)
    cols = {c["name"] for c in insp.get_columns(table)}
    if column.name not in cols:
        with op.batch_alter_table(table) as batch:
            batch.add_column(column)


def upgrade():
    op.create_table(
        "payments",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("registration_id", sa.Integer(), nullable=False),
        sa.Column("provider", sa.Enum("ESEWA", "KHALTI", name="paymentprovider"), nullable=False),
        sa.Column("transaction_id", sa.String(255), nullable=True),
        sa.Column("amount", sa.Float(), nullable=False, server_default="0"),
        sa.Column("currency", sa.String(10), nullable=False, server_default="NPR"),
        sa.Column(
            "status",
            sa.Enum("PENDING", "COMPLETED", "FAILED", "REFUNDED", name="paymentstatus_tx"),
            nullable=False,
            server_default="PENDING",
        ),
        sa.Column("provider_response", sa.JSON(), nullable=True),
        sa.Column("created_at", sa.DateTime(), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
        sa.Column("updated_at", sa.DateTime(), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
        sa.ForeignKeyConstraint(["registration_id"], ["registrations.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("transaction_id"),
    )
    op.create_index("ix_payments_registration", "payments", ["registration_id"])
    op.create_index("ix_payments_provider", "payments", ["provider"])
    op.create_index("ix_payments_status", "payments", ["status"])

    op.create_table(
        "wallets",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("organizer_id", sa.Integer(), nullable=False),
        sa.Column("available_balance", sa.Float(), nullable=False, server_default="0"),
        sa.Column("pending_balance", sa.Float(), nullable=False, server_default="0"),
        sa.Column("created_at", sa.DateTime(), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
        sa.Column("updated_at", sa.DateTime(), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
        sa.ForeignKeyConstraint(["organizer_id"], ["organizer_profiles.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("organizer_id"),
    )

    op.create_table(
        "wallet_transactions",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("wallet_id", sa.Integer(), nullable=False),
        sa.Column(
            "type",
            sa.Enum("TICKET_SALE", "PLATFORM_FEE", "WITHDRAWAL", "REFUND", "ADJUSTMENT",
                    name="wallettxtype"),
            nullable=False,
        ),
        sa.Column("amount", sa.Float(), nullable=False),
        sa.Column("reference_type", sa.String(50), nullable=True),
        sa.Column("reference_id", sa.Integer(), nullable=True),
        sa.Column("description", sa.String(500), nullable=True),
        sa.Column("created_at", sa.DateTime(), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
        sa.ForeignKeyConstraint(["wallet_id"], ["wallets.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_wallet_tx_wallet", "wallet_transactions", ["wallet_id"])
    op.create_index("ix_wallet_tx_type", "wallet_transactions", ["type"])

    op.create_table(
        "withdrawal_requests",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("organizer_id", sa.Integer(), nullable=False),
        sa.Column("wallet_id", sa.Integer(), nullable=True),
        sa.Column("provider", sa.Enum("ESEWA", "KHALTI", name="paymentprovider",
                                      create_type=False), nullable=False),
        sa.Column("account_number", sa.String(100), nullable=False),
        sa.Column("requested_amount", sa.Float(), nullable=False),
        sa.Column("service_fee", sa.Float(), nullable=False, server_default="20"),
        sa.Column("payout_amount", sa.Float(), nullable=False),
        sa.Column(
            "status",
            sa.Enum("PENDING", "APPROVED", "PAID", "REJECTED", name="withdrawalstatus"),
            nullable=False,
            server_default="PENDING",
        ),
        sa.Column("admin_note", sa.Text(), nullable=True),
        sa.Column("transaction_reference", sa.String(255), nullable=True),
        sa.Column("created_at", sa.DateTime(), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
        sa.Column("processed_at", sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(["organizer_id"], ["organizer_profiles.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["wallet_id"], ["wallets.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_withdrawal_organizer", "withdrawal_requests", ["organizer_id"])
    op.create_index("ix_withdrawal_status", "withdrawal_requests", ["status"])

    op.create_table(
        "platform_settings",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("key", sa.String(100), nullable=False),
        sa.Column("value", sa.String(500), nullable=False),
        sa.Column("description", sa.String(500), nullable=True),
        sa.Column("updated_at", sa.DateTime(), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("key"),
    )

    op.create_table(
        "organizer_applications",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("organization_name", sa.String(255), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("verification_info", sa.Text(), nullable=True),
        sa.Column(
            "verification_status",
            sa.Enum("UNDER_REVIEW", "APPROVED", "REJECTED", name="verificationstatus"),
            nullable=False,
            server_default="UNDER_REVIEW",
        ),
        sa.Column("rejection_reason", sa.Text(), nullable=True),
        sa.Column("submitted_at", sa.DateTime(), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
        sa.Column("reviewed_at", sa.DateTime(), nullable=True),
        sa.Column("reviewed_by_admin_id", sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["reviewed_by_admin_id"], ["users.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("user_id"),
    )

    op.create_table(
        "organizer_documents",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("application_id", sa.Integer(), nullable=True),
        sa.Column("filename", sa.String(255), nullable=False),
        sa.Column("stored_path", sa.String(500), nullable=False),
        sa.Column("mime_type", sa.String(120), nullable=True),
        sa.Column("file_size", sa.Integer(), nullable=True),
        sa.Column("created_at", sa.DateTime(), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["application_id"], ["organizer_applications.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_org_docs_user", "organizer_documents", ["user_id"])

    # Backfill columns on pre-existing tables (no-op if already added by ensure_phase1_schema).
    _add_column_if_missing(
        "users",
        sa.Column("account_type", sa.String(20), nullable=False, server_default="USER"),
    )
    _add_column_if_missing(
        "events",
        sa.Column("video_url", sa.String(500), nullable=True),
    )
    _add_column_if_missing(
        "organizer_profiles",
        sa.Column("verification_status", sa.String(20), nullable=False, server_default="UNDER_REVIEW"),
    )
    _add_column_if_missing(
        "organizer_profiles",
        sa.Column("verification_info", sa.Text(), nullable=True),
    )
    _add_column_if_missing(
        "organizer_profiles",
        sa.Column("rejection_reason", sa.Text(), nullable=True),
    )


def downgrade():
    op.drop_index("ix_org_docs_user", table_name="organizer_documents")
    op.drop_table("organizer_documents")
    op.drop_table("organizer_applications")
    op.drop_table("platform_settings")
    op.drop_index("ix_withdrawal_status", table_name="withdrawal_requests")
    op.drop_index("ix_withdrawal_organizer", table_name="withdrawal_requests")
    op.drop_table("withdrawal_requests")
    op.drop_index("ix_wallet_tx_type", table_name="wallet_transactions")
    op.drop_index("ix_wallet_tx_wallet", table_name="wallet_transactions")
    op.drop_table("wallet_transactions")
    op.drop_table("wallets")
    op.drop_index("ix_payments_status", table_name="payments")
    op.drop_index("ix_payments_provider", table_name="payments")
    op.drop_index("ix_payments_registration", table_name="payments")
    op.drop_table("payments")
    sa.Enum(name="paymentprovider").drop(op.get_bind(), checkfirst=True)
    sa.Enum(name="paymentstatus_tx").drop(op.get_bind(), checkfirst=True)
    sa.Enum(name="wallettxtype").drop(op.get_bind(), checkfirst=True)
    sa.Enum(name="withdrawalstatus").drop(op.get_bind(), checkfirst=True)
    sa.Enum(name="verificationstatus").drop(op.get_bind(), checkfirst=True)
