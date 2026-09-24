# EventFlow Backend — Phase 9 (Security sweep + final hardening)

## Leftover routers migrated to central auth

- `user_profile_router` (`GET|PATCH /users/me`) — was 500 (async dep misused).
- `reviews_router` — was always-401; added rating 1–5 validation, event-exists
  check, `GET /reviews/me`; added `GET /user/reviews` for the Reviews page.
- `notifications_router` — was always-401; `/send` was **public** (anyone could
  message any user) → now admin-only with input caps.

## Rate limits (new)

`POST /payments/initiate|/verify` 30/min, `POST /registrations` 60/min,
`POST /organizer/scan` 120/min, `POST /withdrawals` 20/min
(auth already had 20–30/min). Disabled under `EVENTFLOW_TESTING=1` (conftest).

## Standing posture (verified, not just claimed)

Passwords bcrypt-hashed; Bearer JWT (no cookies → no CSRF surface); ORM-only
queries; React-escaped output; QR tokens opaque; verification docs never
statically served; payment secrets backend-only (test creds); `.env` ignored.

## Tests

- New `tests/test_security.py` (14): unauthenticated 401s, user→admin 403s,
  unapproved publish block, cross-organizer/cross-user isolation, notification
  gating, verify-without-initiate, spoofed-success rejection, cross-user pay
  block, capacity, ended-hidden-but-in-history, cancel-blocks-purchase,
  QR reuse on both scan paths, envelope/JSON consistency.
- Full suite: **65 passed**. Frontend `npm run build` ✓.
