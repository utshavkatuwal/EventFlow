# API Documentation

## Base URL

```
http://localhost:8000/api/v1
```

## Authentication

All endpoints (except login/register) require a Bearer token in the Authorization header:

```
Authorization: Bearer <access_token>
```

### Register

```
POST /auth/register
```

Body:

```json
{
  "email": "user@example.com",
  "username": "username",
  "password": "securepassword",
  "first_name": "First",
  "last_name": "Last",
  "phone": "+977-..."
}
```

### Login

```
POST /auth/login
```

Returns `access_token` and `refresh_token`.

### Refresh Token

```
POST /auth/refresh
```

## Events

### List Events (Public)

```
GET /events?page=1&per_page=20&category_id=1&search=term&sort=start_date
```

### Get Event

```
GET /events/{event_id}
```

### Event Stats

```
GET /events/stats
```

### Event Tickets

```
GET /events/{event_id}/tickets
```

## Registration

### Create Registration

```
POST /registrations
```

Body:

```json
{
  "event_id": 1,
  "ticket_type_id": 1
}
```

## Tickets

### Get My Tickets

```
GET /tickets/my
```

### Get Ticket

```
GET /tickets/{ticket_id}
```

## Check-in

### Verify Ticket

```
POST /checkins/verify
```

Body:

```json
{
  "qr_token": "...",
  "scanned_by_user_id": 1
}
```

## Reviews

### Create Review

```
POST /reviews
```

Requires confirmed registration.

## Favorites

### Add Favorite

```
POST /favorites
```

### Remove Favorite

```
DELETE /favorites/{event_id}
```

### Get Saved Events

```
GET /user/saved
```

## Search

```
GET /search?q=term
```

## User Dashboard

### Stats

```
GET /user/stats
```

### Upcoming Events

```
GET /user/upcoming
```

### Past Events

```
GET /user/past
```

### Profile

```
GET /users/me
PATCH /users/me
```

## Organizer Dashboard

### Stats

```
GET /organizer/stats
```

### My Events

```
GET /organizer/events
```

### Registrations

```
GET /organizer/registrations
```

## Admin

### Dashboard Stats

```
GET /admin/stats
```

### Approve Event

```
PATCH /admin/events/{id}/approve
```

### Reject Event

```
PATCH /admin/events/{id}/reject
```

### List Users

```
GET /users
```

### Suspend User

```
PATCH /users/{id}/suspend
```

### List Organizers

```
GET /organizers
```

### Verify Organizer

```
PATCH /organizers/{id}/verify
```

### Reports

```
GET /admin/reports
PATCH /admin/reports/{id}/resolve
```

### Audit Logs

```
GET /admin/audit-logs
```

## Notifications

### List

```
GET /notifications
```

### Mark Read

```
PATCH /notifications/{id}/read
```

### Send (Admin)

```
POST /notifications/send
```
