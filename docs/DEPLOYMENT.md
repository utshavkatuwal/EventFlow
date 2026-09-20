# Deployment Guide

## Docker Deployment (Recommended)

```bash
# Start all services
docker-compose up -d

# Seed database
docker-compose exec backend python scripts/seed.py
```

## Manual Deployment

### Prerequisites

- Python 3.11+
- MySQL 8.0+
- Node.js 18+

### Database Setup

```bash
# Create database
mysql -u root -p -e "CREATE DATABASE eventflow CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;"
```

### Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
# venv\Scripts\activate   # Windows

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your database credentials

# Run migrations
alembic upgrade head

# Seed data (optional)
python scripts/seed.py

# Start server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Start development server
npm run dev
```

The frontend will be available at `http://localhost:5173`.
The API will be available at `http://localhost:8000`.

## Environment Variables

See `.env.example` for all available configuration options.

## Nginx Reverse Proxy (Production)

```nginx
server {
    listen 80;
    server_name eventflow.dev;

    location / {
        proxy_pass http://localhost:5173;
        proxy_set_header Host $host;
    }

    location /api/ {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
    }
}
```

## SSL/TLS

Use Let's Encrypt for free SSL certificates:

```bash
sudo apt install certbot python3-certbot-nginx
sudo certbot --nginx -d eventflow.dev
```

## Production Checklist

- [ ] Set `ENVIRONMENT=production`
- [ ] Set `DEBUG=False`
- [ ] Use strong `SECRET_KEY`
- [ ] Enable HTTPS
- [ ] Configure CORS origins properly
- [ ] Set up database backups
- [ ] Configure logging
- [ ] Set up monitoring
