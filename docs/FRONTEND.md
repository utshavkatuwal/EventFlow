# EventFlow - Frontend Documentation

## Project Structure

```
frontend/
├── src/
│   ├── components/          # Reusable UI components
│   │   ├── Navbar.jsx       # Navigation bar with mobile menu
│   │   ├── Layout.jsx       # Page layout wrapper
│   │   ├── Footer.jsx       # Site footer
│   │   ├── EventCard.jsx    # Event display card
│   │   ├── SimpleEventCard.jsx # Lightweight event card
│   │   ├── Button.jsx       # Button component
│   │   ├── Loading.jsx      # Loading spinner
│   │   ├── ProtectedRoute.jsx # Auth-required route wrapper
│   │   ├── RequireAuth.jsx  # Requires authentication
│   │   ├── RoleGuard.jsx    # Role-based access
│   │   ├── Breadcrumbs.jsx  # Navigation breadcrumbs
│   │   ├── NotificationBadge.jsx # Notification indicator
│   │   ├── Modal.jsx        # Accessible modal dialog
│   │   ├── Avatar.jsx       # User avatar with initials
│   │   ├── Badge.jsx        # Status badges
│   │   ├── Input.jsx        # Form inputs (Input, Textarea, Select)
│   │   └── Table.jsx        # Data table component
│   ├── pages/               # Page components
│   │   ├── HomePage.jsx     # Landing page
│   │   ├── EventsPage.jsx   # Event listing with filters
│   │   ├── EventDetailPage.jsx # Event detail with tickets
│   │   ├── LoginPage.jsx    # User login
│   │   ├── RegisterPage.jsx # User registration
│   │   ├── UserDashboardPage.jsx # User dashboard
│   │   ├── MyTicketsPage.jsx    # User tickets with QR
│   │   ├── SavedEventsPage.jsx  # Saved events
│   │   ├── ReviewsPage.jsx      # User reviews
│   │   ├── UpcomingEventsPage.jsx # Upcoming registered events
│   │   ├── PastEventsPage.jsx   # Past attended events
│   │   ├── ProfilePage.jsx      # User profile view
│   │   ├── ProfileEditPage.jsx  # Edit user profile
│   │   ├── TicketDetailPage.jsx # Ticket with QR code
│   │   ├── CreateEventPage.jsx  # Event creation form
│   │   ├── NotificationsPage.jsx # Notification list
│   │   ├── CheckInPage.jsx      # QR check-in interface
│   │   ├── OrganizerDashboardPage.jsx # Organizer dashboard
│   │   ├── OrganizerMyEventsPage.jsx  # Organizer events list
│   │   ├── OrganizerRegistrationsPage.jsx # Registrations table
│   │   ├── OrganizerAnalyticsPage.jsx   # Analytics dashboard
│   │   ├── OrganizerProfilePage.jsx     # Organizer profile
│   │   ├── AdminDashboardPage.jsx       # Admin dashboard
│   │   ├── AdminEventsPage.jsx          # Admin events management
│   │   ├── AdminUsersPage.jsx           # Admin user management
│   │   ├── AdminOrganizersPage.jsx      # Admin organizer management
│   │   ├── AdminReportsPage.jsx         # Admin reports
│   │   ├── AdminAuditLogsPage.jsx       # Admin audit logs
│   │   └── AdminCategoriesPage.jsx      # Admin categories
│   ├── layouts/             # Page layouts
│   ├── hooks/               # Custom React hooks
│   ├── services/            # API service layer
│   │   └── api.js           # Axios instance with auth
│   ├── context/             # React Context providers
│   │   ├── AuthContext.jsx  # Authentication state
│   │   ├── ApiContext.jsx   # API client
│   │   └── NavContext.jsx   # Navigation state
│   ├── utils/               # Utility functions
│   │   ├── constants.js     # App constants
│   │   └── helpers.js       # Helper functions
│   ├── styles/              # Global CSS and component styles
│   │   ├── global.css       # Design system variables
│   │   └── *.css            # Component-specific styles
│   ├── App.jsx              # Main app with routes
│   └── main.jsx             # Entry point
```

## Key Technologies

- React 18 with functional components and hooks
- Vite for fast development and building
- React Router v6 for client-side routing
- CSS Modules with CSS custom properties for styling
- Axios for API requests with interceptors
- qrcode.react for QR code generation

## State Management

React Context for global state:
- AuthContext: user session, login/logout
- ApiContext: Axios instance with auth headers
- NavContext: mobile menu state

## Routing

All routes defined in App.jsx with lazy loading:
- Public: /, /events, /events/:id, /login, /register
- User: /user/dashboard, /user/tickets/:id, /user/profile, /user/saved, etc.
- Organizer: /organizer/dashboard, /organizer/create-event, /organizer/checkin, etc.
- Admin: /admin/dashboard, /admin/events, /admin/users, etc.

## Styling

CSS custom properties (CSS variables) for design system:
- Colors, spacing, typography, border radius
- Component-specific CSS files alongside components
- Mobile-first responsive design

## API Integration

Axios instance with:
- Base URL configuration
- Request interceptor for auth token
- Response interceptor for 401 handling
- Error handling utilities

## Adding New Pages

1. Create page component in `src/pages/`
2. Add CSS file in `src/styles/`
3. Import in `App.jsx` and add route
4. Add to navigation if needed

## Testing

```bash
npm test
```

Uses Vitest with React Testing Library.

## Building for Production

```bash
npm run build
```

Outputs to `dist/` directory.