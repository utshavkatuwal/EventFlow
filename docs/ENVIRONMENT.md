# EventFlow - Environment Configuration

## Backend Environment Variables

```env
# Database
DATABASE_URL=mysql+pymysql://root:password@localhost:3306/eventflow
DB_HOST=localhost
DB_PORT=3306
DB_NAME=eventflow
DB_USER=root
DB_PASSWORD=your_secure_password_here

# Security
SECRET_KEY=your-super-secret-key-change-this-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7

# CORS
CORS_ORIGINS=http://localhost:5173,http://localhost:3000

# File Upload
UPLOAD_DIRECTORY=uploads/
MAX_UPLOAD_SIZE=10485760

# Application
ENVIRONMENT=development
DEBUG=True
```

## Frontend Environment Variables

```env
VITE_API_URL=http://localhost:8000/api/v1
```

## Docker Environment

```yaml
# docker-compose.yml
services:
  mysql:
    image: mysql:8.0
    environment:
      MYSQL_ROOT_PASSWORD: rootpassword
      MYSQL_DATABASE: eventflow
      MYSQL_USER: eventflow_user
      MYSQL_PASSWORD: eventflow_password

  backend:
    environment:
      DATABASE_URL: mysql+pymysql://eventflow_user:eventflow_password@mysql:3306/eventflow
      DB_HOST: mysql
      SECRET_KEY: your-super-secret-key-change-this-in-production
      CORS_ORIGINS: http://localhost:5173

  frontend:
    environment:
      VITE_API_URL: http://localhost:8000/api/v1
```

## Production Checklist

- [ ] Set `ENVIRONMENT=production`
- [ ] Set `DEBUG=False`
- [ ] Generate strong `SECRET_KEY` (32+ random characters)
- [ ] Use secure database passwords
- [ ] Enable HTTPS with valid SSL certificates
- [ ] Configure CORS for production domains only
- [ ] Set up database backups
- [ ] Configure logging (structured JSON logs)
- [ ] Set up monitoring and alerting
- [ ] Configure rate limiting
- [ ] Set up CI/CD pipeline