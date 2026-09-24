# EventFlow Backend — Phase 2 (Users + Organizer verification)

Extends Phase 1. Frontend glass design preserved; only wired to real APIs.

## Backend (central auth migration)

- `organizer_profile_router.py` — rewritten on `require_auth`; responses now include
  `verification_status / rejection_reason / verification_info`; added
  `GET /organizer/verification-status` for the dashboard banner.
- `organizers_router.py` — admin list with `status` filter, email/phone/business/
  submitted date/verification status/documents; `PATCH /{id}/verify` (compat approve)
  + new `PATCH /{id}/reject` (reason required, audited).
- `users_router.py` — admin list/detail/suspend on `require_admin`; suspend blocks
  self-suspend; returns `account_type` + `roles`.

## Frontend

- `AuthContext` — stores full `user` (account_type + roles + organizer), refresh +
  access tokens, `refreshProfile()` via `GET /auth/me`.
- `ProtectedRoute` — matches `allowedRoles` against `roles[]` OR `account_type`
  (case-insensitive); existing `user/organizer/admin` route guards keep working.
- `LoginPage` — stores server `data.user` + tokens.
- `RegisterPage` — User/Organizer toggle, confirm password, organizer fields
  (business name/description/verification info), calls `/auth/register` or
  `/auth/organizer/register`, shows "currently under review" and routes to dashboard.
- `services/api.js` — `apiUpload()` for FormData docs; errors surface `detail`.
- `OrganizerDashboardPage` — verification banner: UNDER_REVIEW notice + doc upload;
  REJECTED shows reason + resubmit form (re-opens review); APPROVED hides banner.
- `AdminOrganizersPage` — applications table (organizer, email/phone, business,
  submitted, status, docs with auth download, approve/reject + reason prompt).

## Verified

- `pytest tests/test_api.py tests/test_auth.py`: 17 passed; frontend build ok.
- E2E cycle: organizer signup → UNDER_REVIEW → admin list → APPROVE →
  profile APPROVED; reject-without-reason → 400; organizer denied `/users/` → 403.
