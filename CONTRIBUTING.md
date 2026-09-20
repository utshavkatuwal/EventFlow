# EventFlow - Contribution Guide

## Getting Started

1. Fork the repository
2. Clone your fork: `git clone https://github.com/utshavkatuwal/EventFlow.git`
3. Create a feature branch: `git checkout -b feature/your-feature`
4. Make your changes
5. Test your changes
6. Commit with descriptive messages
7. Push and create a Pull Request

## Development Setup

### Backend
```bash
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
# Edit .env with your credentials
alembic upgrade head
python scripts/seed.py
uvicorn app.main:app --reload
```

### Frontend
```bash
cd frontend
npm install
npm run dev
```

## Code Style

### Python (Backend)
- Follow PEP 8
- Use type hints
- Maximum line length: 100 characters
- Run `black` before committing

### JavaScript/React (Frontend)
- Use functional components with hooks
- Use CSS Modules for styling
- Follow React best practices
- Run `eslint` before committing

## Commit Convention

Use conventional commits:
```
feat: add new feature
fix: bug fix
docs: documentation changes
test: add or update tests
refactor: code refactoring
chore: maintenance tasks
```

## Testing

### Backend
```bash
cd backend
pytest tests/ -v
```

### Frontend
```bash
cd frontend
npm test
```

## Pull Request Process

1. Ensure all tests pass
2. Ensure code builds without errors
3. Update documentation if needed
4. Add entry to CHANGELOG.md
5. Request review from maintainers

## Reporting Issues

Use GitHub Issues for bugs and feature requests.