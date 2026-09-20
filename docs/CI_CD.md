# EventFlow - CI/CD Pipeline

## GitHub Actions Workflow

```yaml
# .github/workflows/ci.yml
name: CI/CD Pipeline

on:
  push:
    branches: [master, develop]
  pull_request:
    branches: [master]

jobs:
  backend-tests:
    runs-on: ubuntu-latest
    services:
      mysql:
        image: mysql:8.0
        env:
          MYSQL_ROOT_PASSWORD: rootpassword
          MYSQL_DATABASE: eventflow_test
        ports:
          - 3306:3306
        options: --health-cmd="mysqladmin ping" --health-interval=10s --health-timeout=5s --health-retries=3

    steps:
      - uses: actions/checkout@v4
      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'
      - name: Install dependencies
        run: |
          cd backend
          pip install -r requirements.txt
      - name: Run migrations
        run: |
          cd backend
          alembic upgrade head
        env:
          DATABASE_URL: mysql+pymysql://root:rootpassword@localhost:3306/eventflow_test
      - name: Run tests
        run: |
          cd backend
          pytest tests/ -v --cov=app --cov-report=xml
        env:
          DATABASE_URL: mysql+pymysql://root:rootpassword@localhost:3306/eventflow_test

  frontend-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Set up Node
        uses: actions/setup-node@v4
        with:
          node-version: '18'
      - name: Install dependencies
        run: |
          cd frontend
          npm ci
      - name: Run tests
        run: |
          cd frontend
          npm test
      - name: Build
        run: |
          cd frontend
          npm run build

  lint:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Lint Python
        run: |
          pip install black flake8
          cd backend && black --check . && flake8 app/
      - name: Lint JavaScript
        run: |
          cd frontend && npm run lint

  build-docker:
    needs: [backend-tests, frontend-tests, lint]
    if: github.ref == 'refs/heads/master'
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Build and push backend
        uses: docker/build-push-action@v5
        with:
          context: ./backend
          push: true
          tags: eventflow/backend:latest
      - name: Build and push frontend
        uses: docker/build-push-action@v5
        with:
          context: ./frontend
          push: true
          tags: eventflow/frontend:latest

  deploy:
    needs: build-docker
    if: github.ref == 'refs/heads/master'
    runs-on: ubuntu-latest
    steps:
      - name: Deploy to server
        run: |
          # SSH deployment commands
          echo "Deploying to production..."
```

## Deployment Stages

1. **Development** - Local development with hot reload
2. **Staging** - Feature branches deployed for testing
3. **Production** - Master branch deployed after CI passes

## Environment Promotion

- Feature branch → Staging
- PR to develop → Staging
- Merge to master → Production

## Rollback Strategy

- Keep previous 3 Docker images
- One-click rollback via GitHub Actions
- Database migration rollback with Alembic

## Secrets Management

- GitHub Secrets for API keys, DB passwords
- Environment-specific secrets
- Never commit secrets to repository