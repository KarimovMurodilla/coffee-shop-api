# Quick Start Guide

## Prerequisites

Before you begin, ensure you have:
- **Docker** (version 20.0+)
- **Docker Compose** (version 2.0+)

That's it! Everything else runs in containers.

## Step 1: Clone and Setup

```bash
# Clone the repository
git clone <repository-url>
cd coffee-shop-api

# Copy environment file
cp .env.example .env
```

## Step 2: Configure Environment

Edit `.env` file (optional for development):

```bash
# For development, these defaults work fine
DATABASE_URL=postgresql+asyncpg://postgres:postgres@db:5432/coffee_shop
REDIS_URL=redis://redis:6379/0
SECRET_KEY=your-super-secret-key-change-in-production

# For production, get MailJet credentials from https://www.mailjet.com/
MAILJET_API_KEY=your-mailjet-api-key
MAILJET_API_SECRET=your-mailjet-api-secret
MAILJET_FROM_EMAIL=noreply@coffeeshop.com
```

## Step 3: Start Services

```bash
# Build and start all services
docker-compose up -d

# Check if services are running
docker-compose ps
```

Expected output:
```
NAME                     STATUS              PORTS
coffee-shop-api          running             0.0.0.0:80->80/tcp
coffee-shop-db           running             0.0.0.0:5432->5432/tcp
coffee-shop-redis        running             0.0.0.0:6379->6379/tcp
coffee-shop-celery       running
coffee-shop-celery-beat  running
```

## Step 4: Verify Installation

```bash
# Check API health
curl http://localhost:80/health

# Expected response:
# {"status":"healthy","service":"coffee-shop-api","version":"1.0.0"}
```

## Step 5: Access API Documentation

Open in your browser:
- **Swagger UI**: http://localhost:80/docs
- **ReDoc**: http://localhost:80/redoc

## Step 6: Create First Admin User

```bash
# Run the admin creation script
docker-compose exec api python scripts/create_admin.py
```

Follow the prompts:
```
Enter admin email: admin@coffeeshop.com
Enter admin password: AdminPass123!
Enter first name (optional): Admin
Enter last name (optional): User
```

## Step 7: Test the API

### 1. Register a Regular User

```bash
curl -X POST http://localhost:80/auth/signup \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "UserPass123!",
    "first_name": "John",
    "last_name": "Doe"
  }'
```

### 2. Check Console for Verification Code

```bash
# View API logs to see verification code
docker-compose logs api | grep "VERIFICATION CODE"
```

You'll see something like:
```
VERIFICATION CODE: abc123xyz789...
```

### 3. Verify Email

```bash
curl -X POST http://localhost:80/auth/verify \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "verification_code": "abc123xyz789..."
  }'
```

### 4. Login

```bash
curl -X POST http://localhost:80/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "UserPass123!"
  }'
```

Save the `access_token` from the response.

### 5. Access Protected Endpoint

```bash
curl -X GET http://localhost:80/users/me \
  -H "Authorization: Bearer <your-access-token>"
```

## Using Swagger UI (Easier!)

1. Go to http://localhost:80/docs
2. Click on **POST /auth/signup**
3. Click **"Try it out"**
4. Fill in the request body
5. Click **"Execute"**
6. Copy verification code from console logs
7. Use **POST /auth/verify** to verify
8. Use **POST /auth/login** to get tokens
9. Click **"Authorize"** button (top right)
10. Enter: `Bearer <your-access-token>`
11. Now you can access protected endpoints!

## Common Commands

```bash
# View logs
docker-compose logs -f

# View API logs only
docker-compose logs -f api

# View Celery worker logs
docker-compose logs -f celery_worker

# Restart API service
docker-compose restart api

# Stop all services
docker-compose down

# Stop and remove all data
docker-compose down -v

# Run database migrations
docker-compose exec api alembic upgrade head

# Open Python shell
docker-compose exec api python

# Open PostgreSQL shell
docker-compose exec db psql -U postgres -d coffee_shop
```

## Using Makefile (Even Easier!)

If you have `make` installed:

```bash
make help          # Show all available commands
make up            # Start services
make down          # Stop services
make logs          # View logs
make logs-api      # View API logs
make migrate       # Run migrations
make shell         # Open Python shell
make clean         # Remove everything
```

## Testing Endpoints

### Authentication Flow

```bash
# 1. Signup
SIGNUP_RESPONSE=$(curl -s -X POST http://localhost:80/auth/signup \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"Test123!"}')

echo $SIGNUP_RESPONSE

# 2. Get verification code from logs
docker-compose logs api | grep "VERIFICATION CODE" | tail -1

# 3. Verify (replace with actual code)
curl -X POST http://localhost:80/auth/verify \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","verification_code":"<code-here>"}'

# 4. Login
LOGIN_RESPONSE=$(curl -s -X POST http://localhost:80/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"Test123!"}')

# 5. Extract access token
ACCESS_TOKEN=$(echo $LOGIN_RESPONSE | jq -r '.access_token')

# 6. Access protected endpoint
curl -X GET http://localhost:80/users/me \
  -H "Authorization: Bearer $ACCESS_TOKEN"
```

### Admin Operations

```bash
# Login as admin
ADMIN_LOGIN=$(curl -s -X POST http://localhost:80/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@coffeeshop.com","password":"AdminPass123!"}')

ADMIN_TOKEN=$(echo $ADMIN_LOGIN | jq -r '.access_token')

# Get all users
curl -X GET http://localhost:80/users \
  -H "Authorization: Bearer $ADMIN_TOKEN"

# Get specific user
curl -X GET http://localhost:80/users/1 \
  -H "Authorization: Bearer $ADMIN_TOKEN"

# Update user
curl -X PATCH http://localhost:80/users/1 \
  -H "Authorization: Bearer $ADMIN_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"first_name":"Updated","last_name":"Name"}'

# Delete user
curl -X DELETE http://localhost:80/users/2 \
  -H "Authorization: Bearer $ADMIN_TOKEN"
```

## Troubleshooting

### Services won't start

```bash
# Check if ports are available
lsof -i :80  # API port
lsof -i :5432  # PostgreSQL port
lsof -i :6379  # Redis port

# If ports are in use, stop conflicting services or change ports in docker-compose.yml
```

### Database connection errors

```bash
# Check database is ready
docker-compose exec db pg_isready -U postgres

# Recreate database
docker-compose down -v
docker-compose up -d
```

### Migrations not running

```bash
# Run migrations manually
docker-compose exec api alembic upgrade head

# Check migration status
docker-compose exec api alembic current

# View migration history
docker-compose exec api alembic history
```

### Can't see verification codes

```bash
# Make sure ENVIRONMENT is set to "development" in .env
echo "ENVIRONMENT=development" >> .env

# Restart API service
docker-compose restart api

# Watch logs in real-time
docker-compose logs -f api
```

### Celery tasks not running

```bash
# Check celery worker is running
docker-compose ps celery_worker

# View celery logs
docker-compose logs celery_worker

# Check celery beat is running (schedules periodic tasks)
docker-compose ps celery_beat

# Restart celery services
docker-compose restart celery_worker celery_beat
```

## Development Tips

### Hot Reload

The API automatically reloads when you change code (volume mount in docker-compose.yml).

### Database GUI

Use any PostgreSQL client:
- **Host**: localhost
- **Port**: 5432
- **Database**: coffee_shop
- **Username**: postgres
- **Password**: postgres

Recommended clients:
- DBeaver (cross-platform)
- pgAdmin
- DataGrip

### Redis GUI

Use Redis Desktop Manager or similar:
- **Host**: localhost
- **Port**: 6379

### API Testing

Use Postman, Insomnia, or HTTPie for advanced API testing.

Import the OpenAPI schema from: http://localhost:80/openapi.json

## Next Steps

1. ✅ Start services
2. ✅ Create admin user
3. ✅ Test basic authentication
4. 📝 Read full documentation in README.md
5. 🔧 Customize for your needs
6. 🧪 Add tests
7. 🚀 Deploy to production

## Quick Reference

| Service | URL | Credentials |
|---------|-----|-------------|
| API | http://localhost:80 | - |
| Swagger Docs | http://localhost:80/docs | - |
| ReDoc | http://localhost:80/redoc | - |
| PostgreSQL | localhost:5432 | postgres/postgres |
| Redis | localhost:6379 | - |

## Production Deployment

Before deploying to production:

1. Change `SECRET_KEY` to a strong random value
2. Set up real MailJet credentials
3. Use strong database password
4. Set `ENVIRONMENT=production`
5. Enable HTTPS
6. Configure CORS properly
7. Set up monitoring and logging
8. Implement rate limiting
9. Regular database backups
10. Review security checklist in README.md

---

**Need Help?** Check README.md for detailed documentation or open an issue.
