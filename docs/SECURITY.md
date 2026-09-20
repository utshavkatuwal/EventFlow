# Security

## Data Protection

- Passwords are never stored in plaintext (bcrypt hashing)
- All API endpoints use HTTPS in production
- JWT tokens are signed and validated server-side
- SQL injection prevention via SQLAlchemy ORM (parameterized queries)
- XSS prevention via React auto-escaping

## Input Validation

- All user input validated via Pydantic schemas
- File uploads validated for type, size, and extension
- Search inputs sanitized through ORM

## Token Security

- Access tokens expire in 30 minutes
- Refresh tokens expire in 7 days
- Tokens contain type indicator (access/refresh) preventing substitution attacks
- SECRET_KEY must be kept confidential

## SQL Injection Prevention

All database queries use SQLAlchemy ORM or parameterized queries:

```python
# Safe - parameterized
db.query(User).filter(User.email == email).first()

# Safe - SQLAlchemy handles escaping
db.execute(text("SELECT * FROM users WHERE email = :email"), {"email": email})
```

## CORS Configuration

CORS origins configured via `CORS_ORIGINS` environment variable:

```env
CORS_ORIGINS=http://localhost:5173,http://localhost:3000
```

## Rate Limiting (Future)

Rate limiting should be implemented for:
- Authentication endpoints
- Search endpoints
- File upload endpoints
- Check-in endpoints

## Audit Logging

Sensitive admin operations are recorded in `audit_logs`:
- User suspension
- Event approval/rejection
- Organizer verification
- Report resolution

## File Upload Security

- Maximum file size enforced
- Only allowed extensions: jpg, jpeg, png, gif, webp
- Random filenames generated (no user-provided names)
- Uploads stored outside web root

## Environment Variables

Never commit `.env` files. Use `.env.example` for documentation.

## Common Vulnerabilities Prevented

| Vulnerability | Prevention |
|---------------|------------|
| SQL Injection | SQLAlchemy ORM |
| XSS | React auto-escaping |
| CSRF | JWT tokens (not cookies) |
| Brute Force | Token-based auth (future: rate limiting) |
| Broken Access Control | Role checks on every endpoint |
| Data Exposure | API responses filtered by schema |
