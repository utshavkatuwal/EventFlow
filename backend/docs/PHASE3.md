# EventFlow Backend — Phase 3 (Events: lifecycle, CRUD, discovery)

## Lifecycle (`app/services/lifecycle.py`)

Computed, never stored, never deleted:
`NOW < start → UPCOMING`, `start ≤ NOW < end → ONGOING`, `NOW ≥ end → ENDED`
(missing `end_date` = 4h program). Public discovery hides ENDED/CANCELLED;
user/organizer history keeps everything. Every payload carries `lifecycle`,
`available_capacity`, `category_name`, `organizer_name`.

## Backend

- `events_router.py` rewritten (same paths, auth fixed via central deps):
  - Discovery: `GET /events` with `category_id, q/search, city, date_from/date_to,
    price=free|paid, featured, sort=start_date|newest|popular, include_ended`;
    new `GET /events/featured|upcoming|popular`, `GET /events/stats`,
    `GET /events/{id}` (+ticket types), `GET /events/{id}/tickets`.
  - Management (APPROVED organizer + owner): `POST /events` (DRAFT + default
    General ticket type, ISO-date parsing, category/date validation),
    `PUT /events/{id}`, `PATCH /events/{id}/publish|/cancel`, `DELETE` = soft-cancel
    (closes sales, preserves tickets/ledger).
  - History: `GET /organizer/events?lifecycle=`, `/organizer/registrations`,
    `/user/upcoming|/past` (lifecycle-aware), `/user/stats`, favorites, `/user/saved`.
  - Removed dead duplicates (`/auth/*`, `/users/me`, `/categories`) now canonical elsewhere.
- `events_create_router.py` → deprecated stub (was a shadowed duplicate POST).
- `search_router.py` — fixed crash (`db.query(db.query(...))` join bug), lifecycle
  hide-ended, `category/city/date_from/date_to` filters.
- `categories_router.py` — admin `POST/PATCH/DELETE` (audited, delete blocked if used).
- `tickets_router.py` — `/my` moved before `/{ticket_id}` (was 422 instead of 401).

## Frontend (glass preserved)

- `EventsPage`: server-side category/search/city/date/free-paid filters (debounced).
- `CreateEventPage`: categories from API (id-based), `datetime-local`, DRAFT-only,
  under-review banner.
- `EventDetailPage`: UPCOMING/On-sale/Happening-now/Ended/Cancelled badges, sales closed state.
- `OrganizerMyEventsPage`: UPCOMING/ONGOING/ENDED/CANCELLED tabs + Publish/Cancel buttons.

## Verified

- `pytest tests/`: **24 passed** (was 18; fixed search crash + 3 builtin-`id` email test bugs).
- E2E: approved-organizer create→edit→publish→visible→cancel→hidden→history-kept→soft-delete;
  unapproved create → 403; bad dates → 400. Frontend `npm run build` ✓.
