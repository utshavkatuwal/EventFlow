# Database Schema

## Tables

### users

| Column | Type | Constraints |
|--------|------|-------------|
| id | INT | PK, AUTO_INCREMENT |
| email | VARCHAR(255) | UNIQUE, NOT NULL |
| username | VARCHAR(100) | UNIQUE, NOT NULL |
| password_hash | VARCHAR(255) | NOT NULL |
| first_name | VARCHAR(100) | NULL |
| last_name | VARCHAR(100) | NULL |
| phone | VARCHAR(20) | NULL |
| avatar_url | VARCHAR(500) | NULL |
| is_active | BOOLEAN | DEFAULT TRUE |
| is_email_verified | BOOLEAN | DEFAULT FALSE |
| created_at | DATETIME | DEFAULT NOW() |
| updated_at | DATETIME | DEFAULT NOW() ON UPDATE |

### roles

| Column | Type | Constraints |
|--------|------|-------------|
| id | INT | PK, AUTO_INCREMENT |
| name | VARCHAR(50) | UNIQUE, NOT NULL |
| description | VARCHAR(255) | NULL |
| created_at | DATETIME | DEFAULT NOW() |

### permissions

| Column | Type | Constraints |
|--------|------|-------------|
| id | INT | PK, AUTO_INCREMENT |
| name | VARCHAR(100) | UNIQUE, NOT NULL |
| description | VARCHAR(255) | NULL |
| created_at | DATETIME | DEFAULT NOW() |

### user_roles

| Column | Type | Constraints |
|--------|------|-------------|
| id | INT | PK, AUTO_INCREMENT |
| user_id | INT | FK → users(id), CASCADE |
| role_id | INT | FK → roles(id), CASCADE |
| created_at | DATETIME | DEFAULT NOW() |
| UNIQUE(user_id, role_id) | | |

### role_permissions

| Column | Type | Constraints |
|--------|------|-------------|
| id | INT | PK, AUTO_INCREMENT |
| role_id | INT | FK → roles(id), CASCADE |
| permission_id | INT | FK → permissions(id), CASCADE |
| created_at | DATETIME | DEFAULT NOW() |
| UNIQUE(role_id, permission_id) | | |

### organizer_profiles

| Column | Type | Constraints |
|--------|------|-------------|
| id | INT | PK, AUTO_INCREMENT |
| user_id | INT | FK → users(id), CASCADE, UNIQUE |
| organization_name | VARCHAR(255) | NOT NULL |
| description | TEXT | NULL |
| logo_url | VARCHAR(500) | NULL |
| website | VARCHAR(500) | NULL |
| phone | VARCHAR(20) | NULL |
| address | VARCHAR(500) | NULL |
| city | VARCHAR(100) | NULL |
| country | VARCHAR(100) | DEFAULT 'Nepal' |
| is_verified | BOOLEAN | DEFAULT FALSE |
| created_at | DATETIME | DEFAULT NOW() |
| updated_at | DATETIME | DEFAULT NOW() ON UPDATE |

### event_categories

| Column | Type | Constraints |
|--------|------|-------------|
| id | INT | PK, AUTO_INCREMENT |
| name | VARCHAR(100) | UNIQUE, NOT NULL |
| slug | VARCHAR(120) | UNIQUE, NOT NULL |
| description | VARCHAR(255) | NULL |
| icon | VARCHAR(100) | NULL |
| created_at | DATETIME | DEFAULT NOW() |

### events

| Column | Type | Constraints |
|--------|------|-------------|
| id | INT | PK, AUTO_INCREMENT |
| organizer_id | INT | FK → organizer_profiles(id), CASCADE |
| category_id | INT | FK → event_categories(id), SET NULL |
| title | VARCHAR(255) | NOT NULL |
| slug | VARCHAR(280) | UNIQUE, NOT NULL, INDEX |
| short_description | VARCHAR(500) | NULL |
| full_description | TEXT | NULL |
| cover_image_url | VARCHAR(500) | NULL |
| venue | VARCHAR(500) | NULL |
| address | VARCHAR(500) | NULL |
| city | VARCHAR(100) | NULL |
| country | VARCHAR(100) | DEFAULT 'Nepal' |
| latitude | FLOAT | NULL |
| longitude | FLOAT | NULL |
| start_date | DATE | NOT NULL |
| end_date | DATE | NULL |
| start_time | TIME | NULL |
| end_time | TIME | NULL |
| max_capacity | INT | NOT NULL, DEFAULT 100 |
| status | ENUM | DEFAULT DRAFT |
| is_featured | BOOLEAN | DEFAULT FALSE |
| price_min | FLOAT | DEFAULT 0.0 |
| created_at | DATETIME | DEFAULT NOW() |
| updated_at | DATETIME | DEFAULT NOW() ON UPDATE |
| INDEX idx_events_status | | |
| INDEX idx_events_start_date | | |
| INDEX idx_events_organizer | | |
| INDEX idx_events_category | | |

### event_images

| Column | Type | Constraints |
|--------|------|-------------|
| id | INT | PK, AUTO_INCREMENT |
| event_id | INT | FK → events(id), CASCADE |
| image_url | VARCHAR(500) | NOT NULL |
| is_primary | BOOLEAN | DEFAULT FALSE |
| sort_order | INT | DEFAULT 0 |
| created_at | DATETIME | DEFAULT NOW() |

### ticket_types

| Column | Type | Constraints |
|--------|------|-------------|
| id | INT | PK, AUTO_INCREMENT |
| event_id | INT | FK → events(id), CASCADE |
| name | VARCHAR(100) | NOT NULL |
| description | VARCHAR(500) | NULL |
| price | FLOAT | DEFAULT 0.0 |
| currency | VARCHAR(10) | DEFAULT 'NPR' |
| capacity | INT | NOT NULL, DEFAULT 100 |
| sold_count | INT | DEFAULT 0 |
| sale_start | DATETIME | NULL |
| sale_end | DATETIME | NULL |
| status | ENUM | DEFAULT ACTIVE |
| created_at | DATETIME | DEFAULT NOW() |
| updated_at | DATETIME | DEFAULT NOW() ON UPDATE |

### registrations

| Column | Type | Constraints |
|--------|------|-------------|
| id | INT | PK, AUTO_INCREMENT |
| event_id | INT | FK → events(id), CASCADE |
| user_id | INT | FK → users(id), CASCADE |
| ticket_type_id | INT | FK → ticket_types(id), SET NULL |
| registration_date | DATETIME | DEFAULT NOW() |
| status | ENUM | DEFAULT CONFIRMED |
| payment_status | ENUM | DEFAULT UNPAID |
| amount_paid | FLOAT | DEFAULT 0.0 |
| created_at | DATETIME | DEFAULT NOW() |
| updated_at | DATETIME | DEFAULT NOW() ON UPDATE |
| UNIQUE(event_id, user_id, ticket_type_id) | | |

### tickets (Digital Tickets)

| Column | Type | Constraints |
|--------|------|-------------|
| id | INT | PK, AUTO_INCREMENT |
| registration_id | INT | FK → registrations(id), CASCADE |
| ticket_type_id | INT | FK → ticket_types(id), SET NULL |
| ticket_code | VARCHAR(100) | UNIQUE, NOT NULL |
| qr_token | VARCHAR(255) | UNIQUE, NOT NULL, INDEX |
| qr_code_url | VARCHAR(500) | NULL |
| status | ENUM | DEFAULT VALID |
| checked_in_at | DATETIME | NULL |
| created_at | DATETIME | DEFAULT NOW() |
| updated_at | DATETIME | DEFAULT NOW() ON UPDATE |

### ticket_scans

| Column | Type | Constraints |
|--------|------|-------------|
| id | INT | PK, AUTO_INCREMENT |
| ticket_id | INT | FK → tickets(id), CASCADE |
| scanned_by_user_id | INT | FK → users(id), SET NULL |
| scanned_at | DATETIME | DEFAULT NOW() |
| result | ENUM | NOT NULL |
| notes | TEXT | NULL |

### event_reviews

| Column | Type | Constraints |
|--------|------|-------------|
| id | INT | PK, AUTO_INCREMENT |
| event_id | INT | FK → events(id), CASCADE |
| user_id | INT | FK → users(id), CASCADE |
| registration_id | INT | FK → registrations(id), SET NULL |
| rating | TINYINT | NOT NULL |
| comment | TEXT | NULL |
| is_reported | BOOLEAN | DEFAULT FALSE |
| reported_reason | VARCHAR(500) | NULL |
| is_approved | BOOLEAN | DEFAULT TRUE |
| created_at | DATETIME | DEFAULT NOW() |
| updated_at | DATETIME | DEFAULT NOW() ON UPDATE |
| UNIQUE(event_id, user_id) | | |

### favorites

| Column | Type | Constraints |
|--------|------|-------------|
| id | INT | PK, AUTO_INCREMENT |
| user_id | INT | FK → users(id), CASCADE |
| event_id | INT | FK → events(id), CASCADE |
| created_at | DATETIME | DEFAULT NOW() |
| UNIQUE(user_id, event_id) | | |

### notifications

| Column | Type | Constraints |
|--------|------|-------------|
| id | INT | PK, AUTO_INCREMENT |
| user_id | INT | FK → users(id), CASCADE |
| title | VARCHAR(255) | NOT NULL |
| message | TEXT | NOT NULL |
| type | VARCHAR(50) | NULL |
| reference_type | VARCHAR(50) | NULL |
| reference_id | INT | NULL |
| is_read | BOOLEAN | DEFAULT FALSE |
| created_at | DATETIME | DEFAULT NOW() |

### reports

| Column | Type | Constraints |
|--------|------|-------------|
| id | INT | PK, AUTO_INCREMENT |
| reported_by_user_id | INT | FK → users(id), SET NULL |
| report_type | VARCHAR(50) | NOT NULL |
| reference_type | VARCHAR(50) | NOT NULL |
| reference_id | INT | NOT NULL |
| reason | TEXT | NULL |
| status | ENUM | DEFAULT OPEN |
| resolved_by_admin_id | INT | FK → users(id), SET NULL |
| resolution_note | TEXT | NULL |
| created_at | DATETIME | DEFAULT NOW() |
| updated_at | DATETIME | DEFAULT NOW() ON UPDATE |

### audit_logs

| Column | Type | Constraints |
|--------|------|-------------|
| id | INT | PK, AUTO_INCREMENT |
| admin_user_id | INT | FK → users(id), SET NULL |
| action | VARCHAR(100) | NOT NULL |
| entity_type | VARCHAR(50) | NOT NULL |
| entity_id | INT | NULL |
| details | JSON | NULL |
| ip_address | VARCHAR(45) | NULL |
| created_at | DATETIME | DEFAULT NOW() |

## Relationships

```
users ──1:N── organizer_profiles
users ──N:N── roles (via user_roles)
roles ──N:N── permissions (via role_permissions)
organizer_profiles ──1:N── events
event_categories ──1:N── events
events ──1:N── ticket_types
events ──1:N── event_images
events ──1:N── registrations
ticket_types ──1:N── registrations
ticket_types ──1:N── tickets
registrations ──1:1── tickets
tickets ──1:N── ticket_scans
events ──1:N── event_reviews
users ──1:N── event_reviews
users ──1:N── favorites
events ──1:N── favorites
users ──1:N── notifications
users ──1:N── reports (as reporter)
users ──1:N── audit_logs
```
