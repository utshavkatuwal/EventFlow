# EventFlow Backend — Phase 1 (Foundation: Auth, Roles, Verification tables)

FastAPI + SQLAlchemy. Frontend untouched (React 18 + Vite, Bearer JWT via `localStorage`).

## What Phase 1 delivered

- Central RBAC (`app/auth/dependencies.py`): `require_auth`, `require_roles/admin`,
  `require_organizer_profile`, `require_approved_organizer`, in-memory rate limiting.
- Auth rewrite (`POST /api/v1/auth/register`, `/organizer/register`, `/login`, `/refresh`, `GET /me`):
  full name, email, phone, password + confirm; `account_type` USER/ORGANIZER/ADMIN; JWT carries role.
- Organizer verification (`/api/v1/organizer-applications`): apply/resubmit → UNDER_REVIEW,
  `/me` status, `/me/documents` upload (PDF/JPG/PNG/WEBP ≤10MB, stored in `uploads/verifications/`
  — never public), admin list/approve/reject with required rejection reason + audit log.
- New tables (auto-created + SQLite backfill via `ensure_phase1_schema()` on startup):
  `payments`, `wallets`, `wallet_transactions`, `withdrawal_requests`, `platform_settings`,
  `organizer_applications`, `organizer_documents`; new columns `users.account_type`,
  `organizer_profiles.verification_status/verification_info/rejection_reason`.
- Config (`.env.example`): `FRONTEND_URL`, `BACKEND_URL`, `VERIFICATION_DOC_DIR`,
  eSewa UAT + Khalti test keys (demo only), `PLATFORM_TICKET_FEE=20`,
  `WITHDRAWAL_SERVICE_FEE=20`, `SETTLEMENT_HOLD_DAYS=2`.
- Seed repair: roles admin/organizer/user assigned; dev passwords reset
  (admin@eventflow.dev/admin123, organizer@eventflow.dev/organizer123, user1-2/user123).

## Setup

```bash
cd backend
pip install -r requirements.txt
copy ..\.env.example .env   # then edit SECRET_KEY + DB
python -m uvicorn app.main:app --reload --port 8000
# seed (first run): python scripts/seed.py
```

SQLite dev DB: `backend/eventflow.db`. MySQL via `docker-compose up mysql`.

## Key endpoints

| Method | Path | Auth |
|---|---|---|
| POST | `/api/v1/auth/register` | public, 20/min |
| POST | `/api/v1/auth/organizer/register` | public, 20/min |
| POST | `/api/v1/auth/login` | public, 30/min |
| POST | `/api/v1/auth/refresh` | refresh token |
| GET | `/api/v1/auth/me` | Bearer |
| POST/GET | `/api/v1/organizer-applications`, `/me` | Bearer |
| POST | `/api/v1/organizer-applications/me/documents` | organizer |
| GET/POST | `/api/v1/organizer-applications?...`, `/{id}/review` | admin |

Response envelope: `{success, message, data}` + proper 401/403/429.

## Verification flow

`ORGANIZER signup → UNDER_REVIEW (can login, banner "currently under review", cannot publish)
→ admin APPROVE → full dashboard | REJECT (reason shown) → resubmit re-opens review.`

Docs served backend-only: `GET /{app_id}/documents/{doc_id}/file` (admin).

## Tests

```bash
cd backend
python -m pytest tests/test_api.py tests/test_auth.py -q   # 17 passed
```

Known pre-existing failures (Phase 3–4 scope, untouched legacy routers):
`test_integration.py` search join + registration/event-create token pattern
(`token=Depends(lambda:None)` always None). They will be fixed as each domain
is migrated to central `require_auth` in its phase.

## Next (Phase 2)

Migrate legacy routers to central auth, organizer dashboard banner UI,
admin verification UI wiring, document preview.
