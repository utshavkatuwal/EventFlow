# EventFlow Backend — Phase 7 (Withdrawals: request → manual payout)

## Flow

`Organizer requests (provider + account + amount) → PENDING → admin APPROVE
(optional ack) → admin sends money manually → POST /pay {transaction_reference}
→ PAID + exact-amount ledger → organizer sees reference.`

- Fee math server-side: `payout = requested − withdrawal_service_fee` (Rs.20
  default from `platform_settings`); requests ≤ fee rejected.
- Guards: amount ≤ available − already-requested PENDING/APPROVED (no double
  spend); pay requires reference; reject requires reason; processed requests
  immutable (no double-pay).
- **Ledger**: only PAID writes — one `WITHDRAWAL −requested_amount` row and the
  available balance drops by exactly that amount. Never zeroed, never overwritten.

## Endpoints (`/withdrawals`)

- Organizer (approved): `POST /` (eSewa/Khalti + account + amount),
  `GET /me` history.
- Admin: `GET /?status=`, `POST /{id}/approve|/pay|/reject`.

## Frontend (glass preserved)

- Analytics wallet: Available/Pending + Withdraw form (method radio, account,
  amount) + request history with references.
- New `AdminWithdrawalsPage` (`/admin/withdrawals`): pending queue with
  organizer/amount/fee/payout/account/date, Approve + reference-gated
  **Confirm Manual Payment** + Reject; linked from Admin Dashboard quick-links.

## Verified

- `pytest tests/`: **47 passed** (new `test_withdrawals.py`: 4 — full
  500→480→request-200→pay→280 trail, over/under-fee blocked, reject honesty,
  stranger 403).
- Manual E2E matches. Frontend `npm run build` ✓.
