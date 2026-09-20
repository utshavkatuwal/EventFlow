# Testing Guide

## Backend Tests

```bash
cd backend
pytest tests/ -v
```

### Test Coverage Goals

- Authentication: registration, login, logout, token validation
- Authorization: role-based access, protected routes
- Events: CRUD, search, filtering, capacity enforcement
- Registration: creation, duplicate prevention, capacity limits
- Tickets: generation, QR validation, check-in flow
- Admin: event moderation, user management

## Frontend Tests

```bash
cd frontend
npm test
```

### Test Coverage Goals

- Important components render correctly
- Forms submit properly
- Authentication flows work
- Event registration flow works
- Ticket display shows correct data

## Writing Tests

### Backend Example

```python
def test_user_registration(client, db):
    response = client.post("/api/v1/auth/register", json={
        "email": "test@test.com",
        "username": "testuser",
        "password": "testpass123"
    })
    assert response.status_code == 200
    assert response.json["success"] == True
```

### Frontend Example

```javascript
import { render, screen } from "@testing-library/react";
import HomePage from "../pages/HomePage";

test("renders hero heading", () => {
    render(<HomePage />);
    expect(screen.getByText("Discover Events in Nepal")).toBeInTheDocument();
});
```

## Test Database

Use a separate test database to avoid affecting development data.

Set `TEST_DATABASE_URL` environment variable for test runs.
