# EventFlow - Database Seeding Guide

## Development Seeds

Run the seed script to populate the database with development data:

```bash
cd backend
python scripts/seed.py
```

## Seeded Accounts

| Role | Email | Password | Username |
|------|-------|----------|----------|
| Admin | admin@eventflow.dev | admin123 | admin |
| Organizer | organizer@eventflow.dev | organizer123 | organizer |
| User | user1@test.com | user123 | user1 |
| User | user2@test.com | user123 | user2 |

## Seeded Categories (12)

1. Technology
2. Education
3. Business
4. Music
5. Sports
6. Gaming
7. Arts
8. Career
9. Workshop
10. Conference
11. Community
12. Other

## Seeded Events (8)

1. **Tech Summit Nepal 2026** (Technology, PUBLISHED, Featured)
2. **Business Networking Mixer** (Business, PUBLISHED)
3. **Nepal Music Festival** (Music, PUBLISHED, Featured)
4. **Web Development Workshop** (Workshop, PUBLISHED)
5. **Kathmandu Marathon 2026** (Sports, PENDING_REVIEW)
6. **Future of Education Summit** (Conference, DRAFT)
7. **Career Fair Nepal** (Career, COMPLETED)
8. **Contemporary Art Exhibition** (Arts, PUBLISHED)

## Ticket Types

Each published event gets:
- General ticket (price varies)
- VIP ticket (3x general price or 500 NPR min)

## Usage Notes

- These are development accounts only
- Do not use in production
- Admin can approve/reject pending events
- Organizer can view analytics for their events
- Users can register for published events