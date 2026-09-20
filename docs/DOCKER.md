# EventFlow - Docker Configuration

## Docker Compose for Development

```yaml
# docker-compose.yml
version: "3.9"

services:
  mysql:
    image: mysql:8.0
    container_name: eventflow-mysql
    restart: unless-stopped
    environment:
      MYSQL_ROOT_PASSWORD: ${MYSQL_ROOT_PASSWORD:-rootpassword}
      MYSQL_DATABASE: ${DB_NAME:-eventflow}
      MYSQL_USER: ${DB_USER:-eventflow_user}
      MYSQL_PASSWORD: ${DB_PASSWORD:-eventflow_password}
    ports:
      - "3306:3306"
    volumes:
      - mysql_data:/var/lib/mysql
    command:
      - "--character-set-server=utf8mb4"
      - "--collation-server=utf8mb4_unicode_ci"
    healthcheck:
      test: ["CMD", "mysqladmin", "ping", "-h", "localhost"]
      interval: 10s
      timeout: 5s
      retries: 5

  backend:
    build:
      context: ./backend
      dockerfile: Dockerfile
    container_name: eventflow-backend
    restart: unless-stopped
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=mysql+pymysql://${DB_USER:-eventflow_user}:${DB_PASSWORD:-eventflow_password}@mysql:3306/${DB_NAME:-eventflow}
      - DB_HOST=mysql
      - DB_PORT=3306
      - DB_NAME=${DB_NAME:-eventflow}
      - DB_USER=${DB_USER:-eventflow_user}
      - DB_PASSWORD=${DB_PASSWORD:-eventflow_password}
      - SECRET_KEY=${SECRET_KEY}
      - CORS_ORIGINS=http://localhost:5173
      - UPLOAD_DIRECTORY=/app/uploads/
    volumes:
      - ./backend/uploads:/app/uploads
    depends_on:
      mysql:
        condition: service_healthy
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3

  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile
    container_name: eventflow-frontend
    restart: unless-stopped
    ports:
      - "5173:80"
    depends_on:
      - backend

volumes:
  mysql_data:
```

## Backend Dockerfile

```dockerfile
# backend/Dockerfile
FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    gcc \
    libmariadb-dev \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

## Frontend Dockerfile

```dockerfile
# frontend/Dockerfile
FROM node:18-alpine AS builder

WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
RUN npm run build

FROM nginx:alpine
COPY --from=builder /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
```

## Frontend Nginx Config

```nginx
# frontend/nginx.conf
server {
    listen 80;
    server_name localhost;
    root /usr/share/nginx/html;
    index index.html;

    location / {
        try_files $uri $uri/ /index.html;
    }

    location /api/ {
        proxy_pass http://backend:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

## Environment File

```env
# .env
MYSQL_ROOT_PASSWORD=your_secure_root_password
DB_NAME=eventflow
DB_USER=eventflow_user
DB_PASSWORD=your_secure_db_password
SECRET_KEY=your-super-secret-key-change-this-in-production
CORS_ORIGINS=http://localhost:5173
```

## Production Considerations

- Use secrets management (Docker secrets, HashiCorp Vault)
- Enable SSL/TLS with reverse proxy
- Set up log aggregation (ELK, Loki)
- Configure backup for MySQL volume
- Use multi-stage builds for smaller images
- Scan images for vulnerabilities