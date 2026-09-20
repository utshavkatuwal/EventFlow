# Authentication & Authorization

## Overview

EventFlow uses JWT-based token authentication with access and refresh tokens.

## Token Strategy

| Token | Lifetime | Purpose |
|-------|----------|---------|
| Access Token | 30 minutes | API authentication |
| Refresh Token | 7 days | Obtain new access tokens |

## Password Security

- All passwords are hashed using bcrypt (via passlib)
- Never stored in plaintext
- Minimum 6 characters enforced

## Role System

Three built-in roles:

- **USER**: Browse events, register, manage profile
- **ORGANIZER**: Create/manage events, view analytics, check in attendees
- **ADMIN**: Full platform moderation and management

Roles are assigned via `user_roles` junction table, allowing flexible role assignment.

## Permission Model

Permissions are stored in the `permissions` table and linked to roles via `role_permissions`. This allows easy extension for fine-grained access control.

## Account Status

- `is_active`: Can the user log in?
- `is_email_verified`: Has the user verified their email?

Deactivated accounts cannot authenticate.

## API Security

- All protected endpoints require `Authorization: Bearer <token>` header
- Tokens are validated server-side on every request
- Token expiration is enforced
- Role checks are performed server-side

## Session Management

- Tokens stored in localStorage on frontend
- No server-side sessions (stateless API)
- Logout is client-side token removal
- Refresh tokens can be revoked by changing SECRET_KEY

## Security Best Practices

- HTTPS required in production
- SECRET_KEY must be long and random
- Access tokens should be short-lived
- Refresh tokens should be stored securely
- Implement rate limiting on auth endpoints (future)
