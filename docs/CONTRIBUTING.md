# Contributing

## Development Setup

1. Fork the repository
2. Clone locally
3. Create a feature branch: `git checkout -b feature/your-feature`
4. Make changes
5. Test your changes
6. Commit with descriptive message
7. Push and create Pull Request

## Commit Convention

Use conventional commit messages:

```
feat: add event search functionality
fix: prevent duplicate registrations
docs: update API documentation
test: add authentication tests
refactor: extract event service
chore: update dependencies
```

## Testing

Backend tests:

```bash
cd backend
pytest tests/ -v
```

Frontend tests:

```bash
cd frontend
npm test
```

## Code Style

Backend: Follow PEP 8 guidelines
Frontend: Follow React best practices

## Pull Request Process

1. Ensure tests pass
2. Ensure code builds
3. Update documentation if needed
4. Add changelog entry
5. Request review from maintainers

## Reporting Issues

Use GitHub Issues to report bugs or request features.
