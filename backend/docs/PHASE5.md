# EventFlow Backend — Phase 5 (Payments: eSewa UAT + Khalti test)

## Architecture (provider-independent)

`app/services/payments/{base,esewa,khalti,__init__}` — `get_provider(name)` returns
`ESEWA | KHALTI`; new providers plug in without touching endpoints. Secrets stay
in `.env` (`ESEWA_MERCHANT_CODE/SECRET/BASE_URL`, `KHALTI_SECRET_KEY/BASE_URL`).

- **eSewa v2 UAT**: backend signs form fields (HMAC-SHA256, `total_amount,
  transaction_uuid, product_code`); browser posts to UAT; success redirect
  `?data=<base64>` is verified server-side (signature + `COMPLETE` + amount +
  transaction match). Verification is offline — fully testable with TEST creds.
- **Khalti v2**: backend initiates with secret key → `pidx + payment_url`;
  verify calls Khalti `lookup` (must be `Completed` + paisa-exact). With the
  placeholder key it honestly 400s ("test key not configured") — never faked.

## Endpoints (`/payments`, central auth)

- `POST /initiate {registration_id, provider}` — owner + PENDING only; reuses the
  PENDING row per (order, provider) so retries don't multiply transactions.
- `POST /verify {registration_id, provider, data|pidx}` — verifies, marks
  `COMPLETED`, confirms booking, writes wallet ledger. **Idempotent**: re-verify
  returns the same ticket (`already: true`); tampered amount/signature → 400/402
  and order stays payable.
- `GET /by-registration/{id}`, `GET /wallet` (organizer preview).

`Payment` rows carry provider, transaction_id (unique), amount, status
`PENDING/COMPLETED/FAILED/REFUNDED`, full `provider_response` JSON.

## Wallet on confirm (`services/wallet.py`)

Paid confirm → `TICKET_SALE +gross` and `PLATFORM_FEE −fee` (Rs.20 default from
`platform_settings`, admin-editable) into **pending_balance** (demo: Rs.500 →
Rs.480 pending). Balances only move with ledger rows. Settlement helper moves
matured nets pending → available with `SETTLEMENT` memo rows after
`end + SETTLEMENT_HOLD_DAYS`; runs opportunistically on wallet reads.

## Frontend (glass preserved)

- EventDetail: paid orders show **Pay with eSewa / Khalti** (signed auto-form to
  UAT / full redirect).
- New `PaymentCallbackPage` (`/payments/callback`): forwards provider data to
  `/verify`, shows ticket + links. Failure/timeout states included.

## Verified

- `pytest tests/`: **37 passed** (new `test_payments.py`: 7 — signed initiate,
  verify→ticket+480-pending ledger, double-verify, tampered amount, forged
  signature, Khalti honesty, unknown provider).
- Manual E2E: initiate → signed fields → verify → ticket → wallet 480.0.
- Frontend `npm run build` ✓.
