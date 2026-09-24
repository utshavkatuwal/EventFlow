# EventFlow Backend — Phase 6 (Organizer: attendees, scan, sales, wallet)

## Endpoints (`/organizer`, APPROVED owner only)

- `GET /events/{id}/attendees` — name, email, ticket ID/code, registration date,
  payment status, attendance status/time + stats
  (`tickets_sold/remaining/attended/not_attended/revenue`).
- `POST /scan {qr_token, event_id?}` — hardened gate: ticket exists (token or
  code fallback) → belongs to event → caller owns event (403 otherwise) →
  order CONFIRMED + PAID → ticket VALID → mark USED + `TicketScan SUCCESS`.
  Rescan → `ALREADY_USED` (logged, no state change). Cancelled/expired/unpaid
  each get their own error. Success envelope carries attendee/event/ticket.
- `GET /events/{id}/sales` — per-type sold/remaining/gross + platform fees from
  the ledger + wallet balances.
- `GET /wallet`, `POST /wallet/settle` — ledger view + explicit settlement.
- Legacy `POST /checkins/verify` hardened the same way (ownership derived from
  the ticket's event; unpaid/cancelled blocked; reuse → ALREADY_USED).

Fixed along the way: `ALREADY_USED` detail crashed JSON encoding (raw datetime
→ ISO), `apiFetch` now attaches structured `err.detail` so the scanner UI can
render `TICKET ALREADY USED` with attendee/ticket context.

## Frontend (glass preserved)

- `CheckInPage` — event picker + `/organizer/scan`: VALID TICKET card
  (attendee/event/ticket + ATTENDANCE CONFIRMED) vs ALREADY_USED/invalid states.
- `OrganizerRegistrationsPage` — per-event attendee table with the five stats.
- `OrganizerAnalyticsPage` — wallet (available/pending + recent ledger) and
  sales-by-event (gross/fees/net + type breakdown).

## Verified

- `pytest tests/`: **43 passed** (new `test_organizer_ops.py`: 6 — attendees,
  stranger 403, scan→rescan, wrong-event/invalid, unpaid excluded, sales/wallet).
- Manual E2E: scan 200 CONFIRMED → rescan 400 ALREADY_USED → attendee flips USED.
- Frontend `npm run build` ✓.
