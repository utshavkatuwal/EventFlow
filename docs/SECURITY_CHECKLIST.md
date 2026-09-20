# EventFlow - Security Checklist

## Authentication Security

- [ ] Strong password requirements (min 8 chars, complexity)
- [ ] bcrypt hashing with cost factor 12+
- [ ] JWT tokens with short expiry (30 min access, 7 days refresh)
- [ ] Refresh token rotation
- [ ] Secure token storage (HttpOnly cookies for web)
- [ ] Rate limiting on auth endpoints
- [ ] Account lockout after failed attempts
- [ ] Email verification for registration
- [ ] Password reset with secure tokens
- [ ] Multi-factor authentication (future)

## Authorization Security

- [ ] Role-based access control (RBAC)
- [ ] Resource-level permissions
- [ ] Server-side authorization checks on every endpoint
- [ ] No client-side authorization logic
- [ ] Admin actions require re-authentication

## Data Protection

- [ ] HTTPS enforced in production
- [ ] HSTS headers
- [ ] Secure cookie flags
- [ ] CSRF protection (SameSite cookies, CSRF tokens)
- [ ] Input validation on all endpoints
- [ ] SQL injection prevention (ORM/parameterized queries)
- [ ] XSS prevention (output encoding, CSP)
- [ ] File upload validation (type, size, extension)
- [ ] Secure file storage (outside web root)

## API Security

- [ ] Rate limiting per IP/user
- [ ] Request size limits
- [ ] CORS properly configured
- [ ] Security headers (CSP, X-Frame-Options, etc.)
- [ ] API versioning
- [ ] Audit logging for sensitive operations

## Infrastructure Security

- [ ] Database credentials in secrets manager
- [ ] Regular security updates
- [ ] Firewall rules (least privilege)
- [ ] VPC/network segmentation
- [ ] Database encryption at rest
- [ ] TLS 1.2+ for all connections
- [ ] Secrets rotation policy
- [ ] Backup encryption

## Monitoring & Incident Response

- [ ] Security event logging
- [ ] Failed login alerting
- [ ] Anomalous activity detection
- [ ] Incident response plan
- [ ] Regular security assessments
- [ ] Dependency vulnerability scanning

## Compliance

- [ ] Data retention policy
- [ ] Right to deletion (GDPR)
- [ ] Data portability
- [ ] Privacy policy
- [ ] Terms of service