# EventFlow - Testing Strategy

## Backend Testing

### Test Structure
```
backend/tests/
├── conftest.py              # Pytest fixtures
├── test_api.py              # General API tests
├── test_auth.py             # Authentication tests
├── test_integration.py      # Integration tests
├── test_new_routes.py       # New route tests
└── test_models.py           # Model tests
```

### Running Tests
```bash
cd backend
pytest tests/ -v
pytest tests/ -v --cov=app --cov-report=html
```

### Test Coverage Goals
- Auth: registration, login, logout, token validation, refresh
- Authorization: role-based access, protected routes
- Events: CRUD, search, filtering, capacity enforcement
- Registration: creation, duplicate prevention, capacity limits
- Tickets: generation, QR validation, check-in flow
- Admin: event moderation, user management

### Writing Tests

```python
def test_user_registration(client, db):
    response = client.post("/api/v1/auth/register", json={
        "email": "test@test.com",
        "username": "testuser",
        "password": "testpass123"
    })
    assert response.status_code == 200
    assert response.json()["success"] == True
```

## Frontend Testing

### Test Structure
```
frontend/tests/
├── setup.js                 # Test setup
├── HomePage.test.jsx        # Home page tests
├── auth.test.js             # Auth flow tests
├── events.test.js           # Event discovery tests
├── dashboard.test.js        # Dashboard tests
├── components/              # Component tests
│   ├── EventCard.test.jsx
│   ├── Button.test.jsx
│   └── Modal.test.jsx
```

### Running Tests
```bash
cd frontend
npm test
npm run test:watch
```

### Test Coverage Goals
- Important components render correctly
- Forms submit properly
- Authentication flows work
- Event registration flow works
- Ticket display shows correct data

### Writing Tests

```javascript
import { render, screen } from "@testing-library/react";
import HomePage from "../pages/HomePage";

test("renders hero heading", () => {
    render(<HomePage />);
    expect(screen.getByText("Discover Events in Nepal")).toBeInTheDocument();
});
```

## End-to-End Testing (Future)

Cypress for E2E tests:
- User registration flow
- Event registration and ticket generation
- Organizer event creation
- Admin moderation workflow
- QR check-in process