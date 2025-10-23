# Coffee Shop API - User Management Module

A production-ready user management system built with FastAPI, implementing Clean Architecture principles. This module provides comprehensive user authentication, authorization, and verification functionality.

## 🏗️ Architecture

This project follows **Clean Architecture** principles, separating concerns into distinct layers:

```
app/
├── domain/                 # Enterprise Business Rules
│   ├── entities.py        # Domain entities (User, UserRole)
│   ├── repositories.py    # Repository interfaces
│   └── services.py        # Domain service interfaces
│
├── application/           # Application Business Rules
│   ├── dto.py            # Data Transfer Objects
│   ├── exceptions.py     # Application exceptions
│   └── use_cases/        # Use case implementations
│       ├── auth.py       # Authentication use cases
│       └── user.py       # User management use cases
│
├── infrastructure/        # Frameworks & Drivers
│   ├── database/         # Database implementations
│   │   ├── models.py     # SQLAlchemy models
│   │   └── connection.py # Database connection
│   ├── repositories/     # Repository implementations
│   │   └── user_repository.py
│   ├── services/         # Service implementations
│   │   ├── email_service.py     # MailJet integration
│   │   ├── password_service.py  # Password hashing
│   │   └── token_service.py     # JWT tokens
│   └── celery/          # Background tasks
│       └── worker.py    # Celery worker & tasks
│
├── api/                  # Interface Adapters
│   ├── routes/          # API endpoints
│   │   ├── auth.py      # Authentication endpoints
│   │   └── users.py     # User management endpoints
│   └── dependencies.py  # FastAPI dependencies
│
├── core/                # Configuration
│   └── config.py       # Application settings
│
└── main.py             # Application entry point
```

### Architecture Layers

#### 1. **Domain Layer** (Innermost)
- Contains pure business logic
- No dependencies on external frameworks
- Defines entities, repository interfaces, and domain services
- Independent and testable

#### 2. **Application Layer**
- Implements use cases (business workflows)
- Orchestrates domain objects
- Defines DTOs for data transfer
- Contains application-specific business rules

#### 3. **Infrastructure Layer**
- Implements technical details
- Database access (SQLAlchemy)
- External services (MailJet, JWT, bcrypt)
- Background tasks (Celery)

#### 4. **API Layer** (Outermost)
- FastAPI routes and endpoints
- Request/response handling
- Dependency injection
- HTTP-specific concerns

## ✨ Features

### Authentication & Authorization
- **User Registration** with email validation
- **JWT-based Authentication** (access & refresh tokens)
- **Email Verification** with time-limited codes
- **Role-based Access Control** (User, Admin)
- **Automatic Token Refresh**

### User Management
- **CRUD Operations** for user accounts
- **Profile Updates** (self-service and admin)
- **User Listing** with pagination (admin only)
- **Automatic Cleanup** of unverified users (48 hours)

### Security
- **Password Hashing** with bcrypt
- **JWT Token Validation**
- **Email Uniqueness** enforcement
- **Role-based Permissions**

### Background Tasks
- **Celery Integration** for async tasks
- **Periodic Cleanup** of expired unverified users
- **Email Sending** (development mode prints to console)

## 🚀 Quick Start

### Prerequisites
- Docker & Docker Compose
- Python 3.11+ (for local development)
- MailJet Account (for production email sending)

### Installation

1. **Clone the repository**
```bash
git clone <repository-url>
cd coffee-shop-api
```

2. **Create environment file**
```bash
cp .env.example .env
```

3. **Configure environment variables**
Edit `.env` file with your settings:
```env
POSTGRES_DB=coffee_shop
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
POSTGRES_PORT=5432
POSTGRES_HOST=db

REDIS_URL=redis://redis:6379/0

SECRET_KEY=your-super-secret-key-change-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7

MAILJET_API_KEY=your-mailjet-api-key
MAILJET_API_SECRET=your-mailjet-api-secret
MAILJET_FROM_EMAIL=noreply@coffeeshop.com
MAILJET_FROM_NAME=Coffee Shop

VERIFICATION_CODE_EXPIRE_HOURS=48
ENVIRONMENT=development
```

4. **Start with Docker Compose**
```bash
docker-compose up -d
```

5. **Run database migrations**
```bash
docker-compose exec api alembic upgrade head
```

The API will be available at:
- **API**: http://localhost:80
- **Swagger Docs**: http://localhost:80/docs
- **ReDoc**: http://localhost:80/redoc

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

# Run tests
docker compose exec api pytest
```

## Using Makefile (Even Easier!)

If you have `make` installed:

```bash
# Common Commands

make help          # Show all available commands
make up            # Start services
make down          # Stop services
make logs          # View logs
make logs-api      # View API logs
make migrate       # Run migrations
make generate      # Generate new migration
make shell         # Open Python shell
make clean         # Remove everything
make test          # Run all tests
```


### Local Development (without Docker)

1. **Create virtual environment**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. **Install dependencies**
```bash
pip install -r requirements.txt
```

3. **Run database migrations**
```bash
alembic upgrade head
```

4. **Start the application**
```bash
uvicorn app.main:app --reload
```

5. **Start Celery worker** (in another terminal)
```bash
celery -A app.infrastructure.celery.worker worker --loglevel=info
```

6. **Start Celery beat** (in another terminal)
```bash
celery -A app.infrastructure.celery.worker beat --loglevel=info
```

## 📖 API Documentation

### Authentication Endpoints

#### POST /auth/signup
Register a new user account.

**Request Body:**
```json
{
  "email": "user@example.com",
  "password": "securepassword123",
  "first_name": "John",
  "last_name": "Doe"
}
```

**Response:** `201 Created`
```json
{
  "id": 1,
  "email": "user@example.com",
  "first_name": "John",
  "last_name": "Doe",
  "role": "user",
  "is_verified": false,
  "created_at": "2025-01-01T00:00:00",
  "updated_at": "2025-01-01T00:00:00"
}
```

#### POST /auth/login
Authenticate and receive tokens.

**Request Body:**
```json
{
  "email": "user@example.com",
  "password": "securepassword123"
}
```

**Response:** `200 OK`
```json
{
  "id": 1,
  "email": "user@example.com",
  "first_name": "John",
  "last_name": "Doe",
  "role": "user",
  "is_verified": true,
  "created_at": "2025-01-01T00:00:00",
  "updated_at": "2025-01-01T00:00:00"
}
```

#### POST /auth/refresh
Refresh access token.

**Request Body:**
```json
{
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

**Response:** `200 OK`
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

### User Management Endpoints

All user management endpoints require authentication via Bearer token:
```
Authorization: Bearer <access_token>
```

#### GET /users/me
Get current authenticated user.

**Response:** `200 OK`
```json
{
  "id": 1,
  "email": "user@example.com",
  "first_name": "John",
  "last_name": "Doe",
  "role": "user",
  "is_verified": true,
  "created_at": "2025-01-01T00:00:00",
  "updated_at": "2025-01-01T00:00:00"
}
```

#### GET /users
Get all users (Admin only).

**Query Parameters:**
- `skip` (optional): Number of records to skip (default: 0)
- `limit` (optional): Max records to return (default: 100, max: 500)

**Response:** `200 OK`
```json
[
  {
    "id": 1,
    "email": "user@example.com",
    "first_name": "John",
    "last_name": "Doe",
    "role": "user",
    "is_verified": true,
    "created_at": "2025-01-01T00:00:00",
    "updated_at": "2025-01-01T00:00:00"
  }
]
```

#### GET /users/{id}
Get user by ID (Admin only).

**Response:** `200 OK`
```json
{
  "id": 1,
  "email": "user@example.com",
  "first_name": "John",
  "last_name": "Doe",
  "role": "user",
  "is_verified": true,
  "created_at": "2025-01-01T00:00:00",
  "updated_at": "2025-01-01T00:00:00"
}
```

#### PATCH /users/{id}
Update user information (own account or admin).

**Request Body:**
```json
{
  "first_name": "Jane",
  "last_name": "Smith"
}
```

**Response:** `200 OK`
```json
{
  "id": 1,
  "email": "user@example.com",
  "first_name": "Jane",
  "last_name": "Smith",
  "role": "user",
  "is_verified": true,
  "created_at": "2025-01-01T00:00:00",
  "updated_at": "2025-01-01T00:01:00"
}
```

#### DELETE /users/{id}
Delete user (Admin only).

**Response:** `200 OK`
```json
{
  "message": "User 1 deleted successfully"
}
```

## 🔐 Authentication Flow

1. **Registration**: User signs up with email and password
2. **Verification Code**: System generates and sends verification code (printed to console in dev mode)
3. **Email Verification**: User submits verification code
4. **Login**: User authenticates with email/password
5. **Token Usage**: Client includes access token in Authorization header
6. **Token Refresh**: When access token expires, use refresh token to get new access token

## 🧪 Testing

### Manual Testing with cURL

**1. Register a new user:**
```bash
curl -X POST http://localhost:8000/auth/signup \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "password123",
    "first_name": "Test",
    "last_name": "User"
  }'
```

**2. Check console for verification code, then verify:**
```bash
curl -X POST http://localhost:8000/auth/verify \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "verification_code": "<code-from-console>"
  }'
```

**3. Login:**
```bash
curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "password123"
  }'
```

**4. Access protected endpoint:**
```bash
curl -X GET http://localhost:8000/users/me \
  -H "Authorization: Bearer <access_token>"
```

### Using Swagger UI

Visit http://localhost:8000/docs for interactive API documentation where you can:
- Test all endpoints
- Authenticate and store tokens
- View request/response schemas
- See detailed endpoint descriptions

## 🗄️ Database Migrations

### Create a new migration
```bash
alembic revision --autogenerate -m "Description of changes"
```

### Apply migrations
```bash
alembic upgrade head
```

### Rollback migration
```bash
alembic downgrade -1
```

### View migration history
```bash
alembic history
```

## 🔄 Background Tasks

### Celery Tasks

#### Automatic Cleanup Task
Runs every 6 hours to delete unverified users whose verification code has expired (after 48 hours).

**Manual execution:**
```bash
celery -A app.infrastructure.celery.worker call app.infrastructure.celery.worker.cleanup_unverified_users
```

### Monitoring Celery

**View active workers:**
```bash
celery -A app.infrastructure.celery.worker inspect active
```

**View scheduled tasks:**
```bash
celery -A app.infrastructure.celery.worker inspect scheduled
```

## 🏭 Production Deployment

### Environment Configuration

For production deployment, ensure you:

1. **Change SECRET_KEY** to a strong, random value
2. **Configure MailJet** with valid API credentials
3. **Use PostgreSQL** instead of SQLite
4. **Set ENVIRONMENT** to "production"
5. **Configure CORS** origins in `main.py`
6. **Enable HTTPS** (use reverse proxy like Nginx)
7. **Set up monitoring** and logging

### Docker Production Build

```bash
docker-compose -f docker-compose.prod.yml up -d
```

### Security Checklist

- [ ] Strong SECRET_KEY configured
- [ ] Database credentials secured
- [ ] CORS origins restricted
- [ ] HTTPS enabled
- [ ] Rate limiting implemented
- [ ] Input validation enabled
- [ ] SQL injection prevention (SQLAlchemy ORM handles this)
- [ ] XSS prevention (FastAPI handles this)
- [ ] Environment variables secured

## 📊 Project Structure

```
coffee-shop-api/
├── app/
│   ├── domain/                    # Domain layer (business entities)
│   │   ├── __init__.py
│   │   ├── entities.py           # User entity, UserRole enum
│   │   ├── repositories.py       # Repository interfaces
│   │   └── services.py           # Service interfaces
│   │
│   ├── application/               # Application layer (use cases)
│   │   ├── __init__.py
│   │   ├── dto.py                # Data Transfer Objects
│   │   ├── exceptions.py         # Application exceptions
│   │   └── use_cases/
│   │       ├── __init__.py
│   │       ├── auth.py           # Auth use cases
│   │       └── user.py           # User management use cases
│   │
│   ├── infrastructure/            # Infrastructure layer
│   │   ├── __init__.py
│   │   ├── database/
│   │   │   ├── __init__.py
│   │   │   ├── models.py         # SQLAlchemy models
│   │   │   └── connection.py     # DB connection setup
│   │   ├── repositories/
│   │   │   ├── __init__.py
│   │   │   └── user_repository.py # User repo implementation
│   │   ├── services/
│   │   │   ├── __init__.py
│   │   │   ├── email_service.py   # MailJet integration
│   │   │   ├── password_service.py # Bcrypt hashing
│   │   │   └── token_service.py   # JWT implementation
│   │   └── celery/
│   │       ├── __init__.py
│   │       └── worker.py          # Celery tasks
│   │
│   ├── api/                       # API layer (interface adapters)
│   │   ├── __init__.py
│   │   ├── dependencies.py        # FastAPI dependencies
│   │   └── routes/
│   │       ├── __init__.py
│   │       ├── auth.py            # Auth endpoints
│   │       └── users.py           # User endpoints
│   │
│   ├── core/                      # Core configuration
│   │   ├── __init__.py
│   │   └── config.py              # Settings & config
│   │
│   └── main.py                    # FastAPI app entry point
│
├── alembic/                       # Database migrations
│   ├── versions/
│   │   └── 001_initial_migration.py
│   ├── env.py
│   └── script.py.mako
│
├── tests/                         # Test suite (to be implemented)
│   ├── __init__.py
│   ├── unit/
│   ├── integration/
│   └── e2e/
│
├── scripts/                       # Utility scripts
│   └── create_superuser.py        # Script to create a superuser
│
├── nginx/                         # Nginx configuration
│   └── default.conf               # Nginx default configuration
│
├── .env.example                   # Example environment variables
├── .gitignore                     # Git ignore rules
├── alembic.ini                    # Alembic configuration
├── docker-compose.yml             # Docker Compose config
├── Dockerfile                     # Docker image definition
├── requirements.txt               # Python dependencies
└── README.md                      # This file
```

## 🛠️ Technology Stack

- **Framework**: FastAPI 0.109.0
- **ORM**: SQLAlchemy 2.0.25 (async)
- **Database**: PostgreSQL 15 (SQLite for testing)
- **Authentication**: JWT (python-jose)
- **Password Hashing**: bcrypt (passlib)
- **Email Service**: MailJet API
- **Task Queue**: Celery 5.3.6
- **Message Broker**: Redis 7
- **Migrations**: Alembic 1.13.1
- **Validation**: Pydantic 2.5.3
- **ASGI Server**: Uvicorn 0.27.0
- **Containerization**: Docker & Docker Compose

## 🤝 Development Notes

### Design Decisions

1. **Clean Architecture**: Ensures separation of concerns, testability, and maintainability
2. **Async/Await**: All database operations are asynchronous for better performance
3. **Repository Pattern**: Abstracts data access logic from business logic
4. **Use Case Pattern**: Encapsulates business workflows
5. **Dependency Injection**: Uses FastAPI's DI system for loose coupling

### Future Improvements

With more time, the following enhancements could be implemented:

1. **Comprehensive Test Suite**:
   - Unit tests for domain entities
   - Integration tests for use cases
   - E2E tests for API endpoints
   - Test coverage > 80%

2. **Enhanced Security**:
   - Rate limiting on authentication endpoints
   - Account lockout after failed login attempts
   - Password strength validation
   - Two-factor authentication (2FA)

3. **Advanced Features**:
   - Password reset functionality
   - Email change with verification
   - User activity logging
   - Soft delete for users
   - User profile pictures

4. **Performance**:
   - Redis caching for frequently accessed data
   - Database query optimization
   - Connection pooling tuning
   - CDN for static assets

5. **Monitoring & Logging**:
   - Structured logging (JSON format)
   - Application Performance Monitoring (APM)
   - Error tracking (Sentry integration)
   - Metrics collection (Prometheus)

6. **DevOps**:
   - CI/CD pipeline (GitHub Actions)
   - Automated testing in pipeline
   - Database backup strategy
   - Blue-green deployment

## 📝 License

This project is created for ORB IT technical assessment.

## 👤 Author

Created as part of technical assessment for ORB IT.

## 📧 Support

For questions or issues, please open an issue in the repository.

---

**Note**: In development mode, verification emails are printed to the console instead of being sent via MailJet. To enable actual email sending, set `ENVIRONMENT=production` and configure valid MailJet credentials.json
```
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

### POST /auth/verify
Verify email address.

**Request Body:**
```json
{
  "email": "user@example.com",
  "verification_code": "abc123xyz..."
}
```

**Response:** `200 OK`
```json
{
  "id": 0,
  "email": "string",
  "first_name": "string",
  "last_name": "string",
  "role": "user",
  "is_verified": true,
  "created_at": "2025-10-23T09:42:03.855Z",
  "updated_at": "2025-10-23T09:42:03.855Z"
}
```