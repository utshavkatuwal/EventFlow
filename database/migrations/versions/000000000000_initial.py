"""Initial database schema

Revision ID: 000000000000
Revises:
Create Date: 2026-09-20 00:00:00.000000
"""
from alembic import op
import sqlalchemy as sa
import sqlalchemy.dialects.mysql as mysql_dialect


revision = '000000000000'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # Users table
    op.create_table('users',
        sa.Column('id', mysql_dialect.INTEGER(), autoincrement=True, nullable=False),
        sa.Column('email', sa.String(255), nullable=False),
        sa.Column('username', sa.String(100), nullable=False),
        sa.Column('password_hash', sa.String(255), nullable=False),
        sa.Column('first_name', sa.String(100), nullable=True),
        sa.Column('last_name', sa.String(100), nullable=True),
        sa.Column('phone', sa.String(20), nullable=True),
        sa.Column('avatar_url', sa.String(500), nullable=True),
        sa.Column('is_active', sa.Boolean(), default=True, nullable=False),
        sa.Column('is_email_verified', sa.Boolean(), default=False, nullable=False),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP'), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('email'),
        sa.UniqueConstraint('username')
    )

    # Roles table
    op.create_table('roles',
        sa.Column('id', mysql_dialect.INTEGER(), autoincrement=True, nullable=False),
        sa.Column('name', sa.String(50), nullable=False),
        sa.Column('description', sa.String(255), nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('name')
    )

    # Permissions table
    op.create_table('permissions',
        sa.Column('id', mysql_dialect.INTEGER(), autoincrement=True, nullable=False),
        sa.Column('name', sa.String(100), nullable=False),
        sa.Column('description', sa.String(255), nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('name')
    )

    # User Roles junction
    op.create_table('user_roles',
        sa.Column('id', mysql_dialect.INTEGER(), autoincrement=True, nullable=False),
        sa.Column('user_id', mysql_dialect.INTEGER(), nullable=False),
        sa.Column('role_id', mysql_dialect.INTEGER(), nullable=False),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.ForeignKeyConstraint(['role_id'], ['roles.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('user_id', 'role_id')
    )

    # Role Permissions junction
    op.create_table('role_permissions',
        sa.Column('id', mysql_dialect.INTEGER(), autoincrement=True, nullable=False),
        sa.Column('role_id', mysql_dialect.INTEGER(), nullable=False),
        sa.Column('permission_id', mysql_dialect.INTEGER(), nullable=False),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.ForeignKeyConstraint(['permission_id'], ['permissions.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['role_id'], ['roles.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('role_id', 'permission_id')
    )

    # Organizer Profiles
    op.create_table('organizer_profiles',
        sa.Column('id', mysql_dialect.INTEGER(), autoincrement=True, nullable=False),
        sa.Column('user_id', mysql_dialect.INTEGER(), nullable=False),
        sa.Column('organization_name', sa.String(255), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('logo_url', sa.String(500), nullable=True),
        sa.Column('website', sa.String(500), nullable=True),
        sa.Column('phone', sa.String(20), nullable=True),
        sa.Column('address', sa.String(500), nullable=True),
        sa.Column('city', sa.String(100), nullable=True),
        sa.Column('country', sa.String(100), default='Nepal', nullable=False),
        sa.Column('is_verified', sa.Boolean(), default=False, nullable=False),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP'), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('user_id')
    )

    # Event Categories
    op.create_table('event_categories',
        sa.Column('id', mysql_dialect.INTEGER(), autoincrement=True, nullable=False),
        sa.Column('name', sa.String(100), nullable=False),
        sa.Column('slug', sa.String(120), nullable=False),
        sa.Column('description', sa.String(255), nullable=True),
        sa.Column('icon', sa.String(100), nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('slug'),
        sa.UniqueConstraint('name')
    )

    # Events table
    op.create_table('events',
        sa.Column('id', mysql_dialect.INTEGER(), autoincrement=True, nullable=False),
        sa.Column('organizer_id', mysql_dialect.INTEGER(), nullable=False),
        sa.Column('category_id', mysql_dialect.INTEGER(), nullable=False),
        sa.Column('title', sa.String(255), nullable=False),
        sa.Column('slug', sa.String(280), nullable=False),
        sa.Column('short_description', sa.String(500), nullable=True),
        sa.Column('full_description', sa.Text(), nullable=True),
        sa.Column('cover_image_url', sa.String(500), nullable=True),
        sa.Column('venue', sa.String(500), nullable=True),
        sa.Column('address', sa.String(500), nullable=True),
        sa.Column('city', sa.String(100), nullable=True),
        sa.Column('country', sa.String(100), default='Nepal', nullable=False),
        sa.Column('latitude', sa.Float(), nullable=True),
        sa.Column('longitude', sa.Float(), nullable=True),
        sa.Column('start_date', sa.Date(), nullable=False),
        sa.Column('end_date', sa.Date(), nullable=True),
        sa.Column('start_time', sa.Time(), nullable=True),
        sa.Column('end_time', sa.Time(), nullable=True),
        sa.Column('max_capacity', mysql_dialect.INT(), nullable=False, default=100),
        sa.Column('status', sa.Enum('DRAFT', 'PENDING_REVIEW', 'APPROVED', 'PUBLISHED', 'CANCELLED', 'COMPLETED', 'REJECTED', name='eventstatus'), default='DRAFT', nullable=False),
        sa.Column('is_featured', sa.Boolean(), default=False, nullable=False),
        sa.Column('price_min', sa.Float(), default=0.0, nullable=False),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP'), nullable=False),
        sa.ForeignKeyConstraint(['category_id'], ['event_categories.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['organizer_id'], ['organizer_profiles.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_events_slug', 'events', ['slug'], unique=True)
    op.create_index('idx_events_status', 'events', ['status'], )
    op.create_index('idx_events_start_date', 'events', ['start_date'], )
    op.create_index('idx_events_organizer', 'events', ['organizer_id'], )
    op.create_index('idx_events_category', 'events', ['category_id'], )

    # Event Images
    op.create_table('event_images',
        sa.Column('id', mysql_dialect.INTEGER(), autoincrement=True, nullable=False),
        sa.Column('event_id', mysql_dialect.INTEGER(), nullable=False),
        sa.Column('image_url', sa.String(500), nullable=False),
        sa.Column('is_primary', sa.Boolean(), default=False, nullable=False),
        sa.Column('sort_order', mysql_dialect.INT(), default=0, nullable=False),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.ForeignKeyConstraint(['event_id'], ['events.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )

    # Ticket Types
    op.create_table('ticket_types',
        sa.Column('id', mysql_dialect.INTEGER(), autoincrement=True, nullable=False),
        sa.Column('event_id', mysql_dialect.INTEGER(), nullable=False),
        sa.Column('name', sa.String(100), nullable=False),
        sa.Column('description', sa.String(500), nullable=True),
        sa.Column('price', sa.Float(), default=0.0, nullable=False),
        sa.Column('currency', sa.String(10), default='NPR', nullable=False),
        sa.Column('capacity', mysql_dialect.INT(), nullable=False, default=100),
        sa.Column('sold_count', mysql_dialect.INT(), default=0, nullable=False),
        sa.Column('sale_start', sa.DateTime(), nullable=True),
        sa.Column('sale_end', sa.DateTime(), nullable=True),
        sa.Column('status', sa.Enum('ACTIVE', 'INACTIVE', 'SOLD_OUT', name='ticketstatus'), default='ACTIVE', nullable=False),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP'), nullable=False),
        sa.ForeignKeyConstraint(['event_id'], ['events.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_tickets_event', 'ticket_types', ['event_id'], )

    # Registrations
    op.create_table('registrations',
        sa.Column('id', mysql_dialect.INTEGER(), autoincrement=True, nullable=False),
        sa.Column('event_id', mysql_dialect.INTEGER(), nullable=False),
        sa.Column('user_id', mysql_dialect.INTEGER(), nullable=False),
        sa.Column('ticket_type_id', mysql_dialect.INTEGER(), nullable=False),
        sa.Column('registration_date', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.Column('status', sa.Enum('CONFIRMED', 'PENDING', 'CANCELLED', 'WAITLISTED', name='registrationstatus'), default='CONFIRMED', nullable=False),
        sa.Column('payment_status', sa.Enum('UNPAID', 'PAID', 'REFUNDED', name='paymentstatus'), default='UNPAID', nullable=False),
        sa.Column('amount_paid', sa.Float(), default=0.0, nullable=False),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP'), nullable=False),
        sa.ForeignKeyConstraint(['event_id'], ['events.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['ticket_type_id'], ['ticket_types.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('event_id', 'user_id', 'ticket_type_id', name='uq_registration_event_user_ticket')
    )
    op.create_index('idx_registrations_event', 'registrations', ['event_id'], )
    op.create_index('idx_registrations_user', 'registrations', ['user_id'], )

    # Tickets (Digital Tickets)
    op.create_table('tickets',
        sa.Column('id', mysql_dialect.INTEGER(), autoincrement=True, nullable=False),
        sa.Column('registration_id', mysql_dialect.INTEGER(), nullable=False),
        sa.Column('ticket_type_id', mysql_dialect.INTEGER(), nullable=False),
        sa.Column('ticket_code', sa.String(100), nullable=False),
        sa.Column('qr_token', sa.String(255), nullable=False),
        sa.Column('qr_code_url', sa.String(500), nullable=True),
        sa.Column('status', sa.Enum('VALID', 'USED', 'CANCELLED', 'EXPIRED', name='ticketvalidstatus'), default='VALID', nullable=False),
        sa.Column('checked_in_at', sa.DateTime(), nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP'), nullable=False),
        sa.ForeignKeyConstraint(['registration_id'], ['registrations.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['ticket_type_id'], ['ticket_types.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('ticket_code'),
        sa.UniqueConstraint('qr_token')
    )
    op.create_index('idx_tickets_qr_token', 'tickets', ['qr_token'], unique=True)

    # Ticket Scans (Audit trail)
    op.create_table('ticket_scans',
        sa.Column('id', mysql_dialect.INTEGER(), autoincrement=True, nullable=False),
        sa.Column('ticket_id', mysql_dialect.INTEGER(), nullable=False),
        sa.Column('scanned_by_user_id', mysql_dialect.INTEGER(), nullable=False),
        sa.Column('scanned_at', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.Column('result', sa.Enum('SUCCESS', 'FAILED', name='scanresult'), nullable=False),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.ForeignKeyConstraint(['ticket_id'], ['tickets.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['scanned_by_user_id'], ['users.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id')
    )

    # Event Reviews
    op.create_table('event_reviews',
        sa.Column('id', mysql_dialect.INTEGER(), autoincrement=True, nullable=False),
        sa.Column('event_id', mysql_dialect.INTEGER(), nullable=False),
        sa.Column('user_id', mysql_dialect.INTEGER(), nullable=False),
        sa.Column('registration_id', mysql_dialect.INTEGER(), nullable=True),
        sa.Column('rating', mysql_dialect.TINYINT(), nullable=False),
        sa.Column('comment', sa.Text(), nullable=True),
        sa.Column('is_reported', sa.Boolean(), default=False, nullable=False),
        sa.Column('reported_reason', sa.String(500), nullable=True),
        sa.Column('is_approved', sa.Boolean(), default=True, nullable=False),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP'), nullable=False),
        sa.ForeignKeyConstraint(['event_id'], ['events.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['registration_id'], ['registrations.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('event_id', 'user_id', name='uq_review_event_user')
    )
    op.create_index('idx_reviews_event', 'event_reviews', ['event_id'], )

    # Favorites
    op.create_table('favorites',
        sa.Column('id', mysql_dialect.INTEGER(), autoincrement=True, nullable=False),
        sa.Column('user_id', mysql_dialect.INTEGER(), nullable=False),
        sa.Column('event_id', mysql_dialect.INTEGER(), nullable=False),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.ForeignKeyConstraint(['event_id'], ['events.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('user_id', 'event_id', name='uq_favorite_user_event')
    )
    op.create_index('idx_favorites_user', 'favorites', ['user_id'], )

    # Notifications
    op.create_table('notifications',
        sa.Column('id', mysql_dialect.INTEGER(), autoincrement=True, nullable=False),
        sa.Column('user_id', mysql_dialect.INTEGER(), nullable=False),
        sa.Column('title', sa.String(255), nullable=False),
        sa.Column('message', sa.Text(), nullable=False),
        sa.Column('type', sa.String(50), nullable=True),
        sa.Column('reference_type', sa.String(50), nullable=True),
        sa.Column('reference_id', mysql_dialect.INTEGER(), nullable=True),
        sa.Column('is_read', sa.Boolean(), default=False, nullable=False),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_notifications_user', 'notifications', ['user_id'], )

    # Reports
    op.create_table('reports',
        sa.Column('id', mysql_dialect.INTEGER(), autoincrement=True, nullable=False),
        sa.Column('reported_by_user_id', mysql_dialect.INTEGER(), nullable=False),
        sa.Column('report_type', sa.String(50), nullable=False),
        sa.Column('reference_type', sa.String(50), nullable=False),
        sa.Column('reference_id', mysql_dialect.INTEGER(), nullable=False),
        sa.Column('reason', sa.Text(), nullable=True),
        sa.Column('status', sa.Enum('OPEN', 'REVIEWED', 'RESOLVED', 'DISMISSED', name='reportstatus'), default='OPEN', nullable=False),
        sa.Column('resolved_by_admin_id', mysql_dialect.INTEGER(), nullable=True),
        sa.Column('resolution_note', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP'), nullable=False),
        sa.ForeignKeyConstraint(['reported_by_user_id'], ['users.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['resolved_by_admin_id'], ['users.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id')
    )

    # Audit Logs
    op.create_table('audit_logs',
        sa.Column('id', mysql_dialect.INTEGER(), autoincrement=True, nullable=False),
        sa.Column('admin_user_id', mysql_dialect.INTEGER(), nullable=False),
        sa.Column('action', sa.String(100), nullable=False),
        sa.Column('entity_type', sa.String(50), nullable=False),
        sa.Column('entity_id', mysql_dialect.INTEGER(), nullable=True),
        sa.Column('details', sa.JSON(), nullable=True),
        sa.Column('ip_address', sa.String(45), nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.ForeignKeyConstraint(['admin_user_id'], ['users.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id')
    )


def downgrade():
    op.drop_table('audit_logs')
    op.drop_table('reports')
    op.drop_table('notifications')
    op.drop_table('favorites')
    op.drop_table('event_reviews')
    op.drop_table('ticket_scans')
    op.drop_table('tickets')
    op.drop_table('registrations')
    op.drop_table('ticket_types')
    op.drop_table('event_images')
    op.drop_table('events')
    op.drop_table('event_categories')
    op.drop_table('organizer_profiles')
    op.drop_table('role_permissions')
    op.drop_table('user_roles')
    op.drop_table('permissions')
    op.drop_table('roles')
    op.drop_table('users')
