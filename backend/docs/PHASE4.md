# EventFlow Backend — Phase 4 (Tickets: booking, capacity, QR)

## Booking engine (`app/services/booking.py`)

`User → PENDING order → free? CONFIRMED+ticket now : PENDING → (Phase 5 payment) → CONFIRMED+ticket`
- One transaction with `SELECT … FOR UPDATE` on the ticket-type row: no oversell,
  no purchase after ENDED/CANCELLED/off-sale, sale-window enforced.
- Duplicate guard → 409; cancelled orders are *revived* on rebook (unique
  constraint spans all statuses; old CANCELLED ticket rows kept for audit, fresh
  ticket issued on confirm).
- `confirm_booking()` is idempotent (Phase 5 entry point).

## Tickets

- `secrets.token_urlsafe(32)` QR token (opaque, no PII); `EV-XXXXXX` codes;
  QR PNG (`qrcode` lib) at `uploads/tickets/*.png`, served via
  `StaticFiles /uploads/tickets` (verification docs stay unmounted).
- `VALID → USED` (Phase 6) / `CANCELLED`; cancel frees capacity (`sold_count--`).

## Endpoints (central auth)

- `POST /registrations` (+ legacy alias in events_router for EventDetailPage):
  free → ticket immediately; paid → `{payment_required, amount, registration_id}`.
- `GET /registrations/me|/{id}`, `POST /registrations/{id}/cancel` (USED tickets can't cancel).
- `GET /tickets/my|/{id}` — owner, event organizer, or admin only (was: any authed user).
- `user_router` rewritten: `/user/stats|upcoming|past|saved|me` + `PATCH /user/me`
  (was always-401; dashboard zeros fixed). Added `GET /users/me` compat.

## Frontend (glass preserved)

- EventDetail: numeric event_id, PENDING vs issued messaging (no more `alert()`).
- MyTickets: ticket code, payment status, Details link; QR still client-rendered
  from `qr_token`.

## Verified

- `pytest tests/`: **30 passed** (new `test_booking.py`: 6 — free/duplicate/pending/
  sold-out/ended/cancel-rebook/visibility; `conftest.py` disables rate limits in-suite).
- Manual E2E: free→ticket+PNG on disk, paid→PENDING, cancel→rebook→fresh order.
- Frontend `npm run build` ✓.
