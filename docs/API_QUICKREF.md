# EventFlow - API Quick Reference

## Base URL
```
http://localhost:8000/api/v1
```

## Authentication
```
POST /auth/register - Register new user
POST /auth/login - Login and get tokens
POST /auth/refresh - Refresh access token
```

## User Profile
```
GET /users/me - Get current user profile
PATCH /users/me - Update current user profile
```

## Organizer Profile
```
GET /organizer/profile - Get organizer profile
PATCH /organizer/profile - Update organizer profile
```

## Events
```
GET /events - List events (with filters)
GET /events/stats - Event statistics
GET /events/{id} - Get event details
GET /events/{id}/tickets - Get event ticket types
POST /events - Create event (organizer)
```

## Categories
```
GET /categories - List all categories
GET /categories/{id} - Get category details
```

## Registration & Tickets
```
POST /registrations - Register for event (requires auth)
GET /tickets/my - Get my tickets
GET /tickets/{id} - Get ticket details with QR
```

## Check-in
```
POST /checkins/verify - Verify QR code (organizer)
```

## Favorites
```
POST /favorites - Save event
DELETE /favorites/{event_id} - Remove saved event
GET /user/saved - Get saved events
```

## User Dashboard
```
GET /user/stats - Dashboard statistics
GET /user/upcoming - Upcoming events
GET /user/past - Past events
GET /user/notifications - User notifications
```

## Organizer Dashboard
```
GET /organizer/stats - Organizer statistics
GET /organizer/events - My events
GET /organizer/registrations - Event registrations
```

## Admin
```
GET /admin/stats - Platform statistics
GET /admin/events - All events
PATCH /admin/events/{id}/approve - Approve event
PATCH /admin/events/{id}/reject - Reject event
GET /users - List all users
PATCH /users/{id}/suspend - Suspend/activate user
GET /organizers - List organizers
PATCH /organizers/{id}/verify - Verify organizer
GET /admin/reports - List reports
PATCH /admin/reports/{id}/resolve - Resolve report
GET /admin/audit-logs - Audit logs
GET /admin/categories - Manage categories
POST /admin/categories - Add category
```

## Notifications
```
GET /notifications - List notifications
PATCH /notifications/{id}/read - Mark as read
POST /notifications/send - Send notification (admin)
```

## Search
```
GET /search?q=term - Search events
```

## Reviews
```
POST /reviews - Create review (requires attended event)
```