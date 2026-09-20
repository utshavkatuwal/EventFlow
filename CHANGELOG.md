# EventFlow Changelog

## v1.0.0 (In Development)

### Backend
- FastAPI application with modular router architecture
- JWT authentication (access + refresh tokens)
- User registration and login
- Event CRUD with search, filter, pagination
- Category management
- Ticket type configuration
- Registration workflow with capacity enforcement
- Digital ticket generation with QR token
- QR check-in validation
- Review system with duplicate prevention
- Notification system (in-app)
- Admin moderation tools
- Organizer dashboard data
- File upload handling with validation

### Frontend
- React 18 with Vite
- React Router v6 with protected routes
- Global CSS design system
- Responsive Navbar with mobile menu
- Event discovery (Home, Events, Event Detail)
- Auth pages (Login, Register)
- Dashboard layouts (User, Organizer, Admin)
- Ticket display with QR code rendering
- Check-in interface
- User profile page
- Breadcrumbs navigation
- Context-based state management (Auth, API, Nav)

### Database
- 18 tables with proper relationships
- Full migration support via Alembic
- Development seed script with sample data

### Documentation
- API documentation
- Architecture overview
- Database schema reference
- Authentication guide
- Deployment guide
- Security guide
- Testing guide
- Contribution guidelines
- Project structure documentation
