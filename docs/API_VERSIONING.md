# EventFlow - API Versioning Strategy

## Versioning Approach

We use URL path versioning: `/api/v1/`, `/api/v2/`, etc.

## Current Version

**v1** - Stable API for all clients (Web, future Flutter mobile)

## Version Lifecycle

1. **v1** - Current stable version
   - All core features implemented
   - Backward compatible changes only
   - Long-term support

2. **v2** (Future) - Major breaking changes
   - New authentication (OAuth2, social login)
   - GraphQL endpoint
   - Real-time subscriptions
   - Payment integration
   - Multi-tenant support

## Deprecation Policy

- Minimum 6 months notice before deprecating endpoints
- Deprecated endpoints return `Sunset` header
- Migration guide provided for each breaking change
- Old version supported during transition period

## Client Compatibility

Clients should:
- Accept unknown fields in responses (forward compatibility)
- Handle missing optional fields gracefully
- Implement exponential backoff for retries
- Cache responses appropriately

## Version Header

For debugging, responses include:
```
X-API-Version: v1
```