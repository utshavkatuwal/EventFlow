# EventFlow Backend

FastAPI + SQLAlchemy event discovery, ticketing, organizer and admin platform.
Glass React frontend lives in `../frontend` (untouched by backend phases).

## Setup

```bash
cd backend
pip install -r requirements.txt
copy ..\.env.example .env   # then set SECRET_KEY + DATABASE_URL
python scripts/seed.py      # creates tables + categories + demo accounts
python -m uvicorn app.main:app --reload --port 8000
```

- Swagger: http://localhost:8000/docs · ReDoc: /redoc · Health: /health
- SQLite dev DB: `eventflow.db`. MySQL: `docker-compose up mysql` + set `DATABASE_URL`.
- `ensure_phase1_schema()` runs on startup: creates new tables, backfills
  `users.account_type` / organizer verification columns, seeds roles + platform
  settings, repairs stale dev password hashes.

## Database

Tables: `users, roles, user_roles, event_categories, events, event_images,
organizer_profiles, organizer_applications, organizer_documents,
ticket_types, registrations, tickets, ticket_scans, payments,
wallets, wallet_transactions, withdrawal_requests, platform_settings,
event_reviews, favorites, notifications, reports, audit_logs`.

Key indexes: user email, event organizer/category/dates, ticket token+code,
payment transaction_id, withdrawal status, registration (user/event).
Ended events are never deleted — lifecycle is computed, history preserved.

## Environment

| Var | Meaning |
|---|---|
| `DATABASE_URL` | SQLAlchemy URL (sqlite file or `mysql+pymysql://…`) |
| `SECRET_KEY/ALGORITHM` | JWT signing (access 30min, refresh 7d) |
| `CORS_ORIGINS/FRONTEND_URL/BACKEND_URL` | web + redirect targets |
| `ESEWA_MERCHANT_CODE/SECRET/BASE_URL` | eSewa **UAT** (demo only) |
| `KHALTI_SECRET_KEY/BASE_URL` | Khalti sandbox key (**test only**) |
| `PLATFORM_TICKET_FEE/WITHDRAWAL_SERVICE_FEE/SETTLEMENT_HOLD_DAYS` | defaults, admin-editable |
| `VERIFICATION_DOC_DIR/MAX_UPLOAD_SIZE` | private doc storage, 10MB cap |

`.env` is git-ignored; never commit secrets.

## API (all under `/api/v1`, envelope `{success,message,data/items}`)

| Area | Endpoints |
|---|---|
| Auth | `POST /auth/register`, `/auth/organizer/register`, `/auth/login`, `/auth/refresh`, `GET /auth/me` |
| Verification | `POST|GET /organizer-applications`, `/me`, `/me/documents`, admin `GET /`, `/{id}/review`, doc download |
| Events | `GET /events` (filters), `/events/featured|upcoming|popular|stats|{id}|{id}/tickets`; organizer `POST /events`, `PUT /{id}`, `PATCH /{id}/publish|/cancel`, `DELETE` (soft) |
| Categories | `GET /categories[/{id}]`, admin `POST/PATCH/DELETE` |
| Search | `GET /search?q=` (+category/city/dates) |
| Tickets | `POST /registrations`, `GET /registrations/me|/{id}`, `POST /{id}/cancel`, `GET /tickets/my|/{id}` |
| Payments | `POST /payments/initiate|/verify`, `GET /by-registration/{id}`, `GET /wallet` |
| Organizer | `/organizer/events[/{id}/attendees|/sales]`, `/organizer/registrations|/stats`, `POST /organizer/scan`, `/organizer/wallet[/settle]`, legacy `POST /checkins/verify` |
| Withdrawals | organizer `POST /withdrawals`, `GET /me`; admin `GET /`, `POST /{id}/approve|/pay|/reject` |
| Admin | `GET /stats|/events|/payments|/wallets|/settings|/reports|/audit-logs`, `PATCH /events/{id}/approve|/reject`, `/reports/{id}/resolve`, `PATCH /settings` |
| Users | admin `GET /users[/{id}]`, `PATCH /{id}/suspend`; self `GET|PATCH /user/me`, `/user/stats|upcoming|past|saved` |

## Authentication & roles

Bearer JWT (`role` + `account_type` claims). Central deps in
`app/auth/dependencies.py`: `require_auth`, `require_roles/admin`,
`require_organizer_profile`, `require_approved_organizer` (+ rate limits on
auth endpoints). Frontend guards are cosmetic — every protected endpoint
re-checks server-side.

## Organizer verification

Signup → `UNDER_REVIEW` (login OK, banner shown, publishing 403) → admin
approve → `APPROVED` full dashboard; reject carries a reason and resubmission
(including new doc upload) re-opens review. Docs: PDF/JPG/PNG/WEBP ≤10MB in
`uploads/verifications/` (never statically served; admin-only download).

## Payments (TEST/UAT)

Provider interface in `app/services/payments/` (eSewa HMAC redirect-response,
Khalti initiate+lookup). Backend signs/verifies everything; frontend success
screens mean nothing until `/verify` confirms. Callbacks idempotent
(`already: true`, no duplicate tickets/ledger). No secrets in React.

## Wallet

`wallets(available/pending)` + `wallet_transactions` ledger — balances move
only with rows (`TICKET_SALE +gross`, `PLATFORM_FEE −fee` → pending on confirm;
`WITHDRAWAL −exact` on admin payout; `ADJUSTMENT` settlement memos).
Settlement after `end + hold_days` (opportunistic on reads + explicit endpoint).

## QR tickets

`secrets`-random token (no PII) + `EV-XXXXXX` code + PNG in
`uploads/tickets/` (mounted read-only). Scan enforces existence, event
ownership, CONFIRMED+PAID, single use (`USED` + audit `ticket_scans`).

## Development

```bash
cd backend
python -m pytest tests/ -q        # full suite
cd ../frontend && npm run build    # frontend check
```

Demo accounts (dev only): `admin@eventflow.dev/admin123`,
`organizer@eventflow.dev/organizer123`, `user1@test.com/user123`.
Phase docs: `docs/PHASE1.md` … `docs/PHASE8.md`.
