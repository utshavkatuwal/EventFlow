# EventFlow Backend — Phase 8 (Admin control plane + docs)

## Fixed (were 500s)

- `admin_router` used `user.role` (no such column) → every admin call crashed;
  rewritten on central `require_admin`.
- `analytics_service` missed `Report`/`datetime` imports → `/admin/stats` crashed;
  organizer stats had the same latent `datetime` bug.
- Shadowed duplicates (`/admin/stats`, `/admin/events` in events_router) removed —
  admin_router is now canonical.

## New

- `GET /admin/stats`: users, organizers (pending/approved), events
  (total/active/ended/cancelled/published/pending), tickets sold, attendees,
  transaction volume, wallet available/pending totals, withdrawals
  (pending count+amount, completed volume), reviews, open reports.
- `GET /admin/payments` (provider/status filters + volume),
  `GET /admin/wallets` (per-organizer balances).
- `GET|PATCH /admin/settings` — `withdrawal_service_fee`, `platform_ticket_fee`,
  `settlement_hold_days` (validated, audited; negative rejected).
- Kept: event approve/reject, reports, audit logs (fixed guards).

## Frontend (glass preserved)

- Admin dashboard: 12 stat cards, quick-links (incl. withdrawals), event table,
  inline platform-settings editor.

## Docs

- `backend/README.md` rewritten: setup, database, env table, full API map, auth,
  verification, payments, wallet, QR, dev accounts, phase index.

## Verified

- `pytest`: **51 passed** full suite (`test_admin.py`: 4 new).
- Frontend `npm run build` ✓.
