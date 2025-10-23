# Coffee Shop API - User Management Module

A production-ready user management system built with FastAPI, implementing Clean Architecture principles. This module provides comprehensive user authentication, authorization, and verification functionality.

## 🏗️ Architecture

This project follows **Clean Architecture** principles, separating concerns into distinct layers:

```
coffee-shop-api/
│
├── app/                                    # Main application package
│   ├── __init__.py
│   │
│   ├── domain/                            # Domain Layer (Clean Architecture)
│   │   ├── __init__.py
│   │   ├── entities.py                    # User entity, UserRole enum
│   │   ├── repositories.py                # UserRepository interface
│   │   └── services.py                    # EmailService, PasswordService, TokenService interfaces
│   │
│   ├── application/                       # Application Layer (Use Cases)
│   │   ├── __init__.py
│   │   ├── dto.py                         # Request/Response DTOs
│   │   ├── exceptions.py                  # Application exceptions
│   │   └── use_cases/
│   │       ├── __init__.py
│   │       ├── auth.py                    # SignupUseCase, LoginUseCase, RefreshTokenUseCase, VerifyEmailUseCase
│   │       └── user.py                    # GetCurrentUserUseCase, GetAllUsersUseCase, GetUserByIdUseCase, 
│   │                                      # UpdateUserUseCase, DeleteUserUseCase, CleanupUnverifiedUsersUseCase
│   │
│   ├── infrastructure/                    # Infrastructure Layer (Implementations)
│   │   ├── __init__.py
│   │   │
│   │   ├── database/
│   │   │   ├── __init__.py
│   │   │   ├── models.py                  # SQLAlchemy UserModel
│   │   │   └── connection.py              # Database engine and session factory
│   │   │
│   │   ├── repositories/
│   │   │   ├── __init__.py
│   │   │   └── user_repository.py         # SQLAlchemyUserRepository implementation
│   │   │
│   │   ├── services/
│   │   │   ├── __init__.py
│   │   │   ├── email_service.py           # MailJetEmailService implementation
│   │   │   ├── password_service.py        # BcryptPasswordService implementation
│   │   │   └── token_service.py           # JWTTokenService implementation
│   │   │
│   │   └── celery/
│   │       ├── __init__.py
│   │       └── worker.py                  # Celery app and cleanup_unverified_users task
│   │
│   ├── api/                               # API Layer (Interface Adapters)
│   │   ├── __init__.py
│   │   ├── dependencies.py                # FastAPI dependency injection functions
│   │   └── routes/
│   │       ├── __init__.py
│   │       ├── auth.py                    # POST /auth/signup, /auth/login, /auth/refresh, /auth/verify
│   │       └── users.py                   # GET /users/me, /users, /users/{id}
│   │                                      # PATCH /users/{id}, DELETE /users/{id}
│   │
│   ├── core/                              # Core Configuration
│   │   ├── __init__.py
│   │   └── config.py                      # Settings class with Pydantic
│   │
│   └── main.py                            # FastAPI application entry point
│
├── alembic/                               # Database Migrations
│   ├── versions/
│   │   ├── __init__.py
│   │   └── 001_initial_migration.py       # Initial users table migration
│   ├── env.py                             # Alembic environment configuration
│   └── script.py.mako                     # Migration template
│
├── tests/                                 # Test Suite (to be implemented)
│   ├── __init__.py
│   ├── unit/                              # Unit tests
│   │   ├── __init__.py
│   │   ├── test_entities.py
│   │   └── test_use_cases.py
│   ├── integration/                       # Integration tests
│   │   ├── __init__.py
│   │   ├── test_repositories.py
│   │   └── test_services.py
│   └── e2e/                               # End-to-end tests
│       ├── __init__.py
│       └── test_api.py
│
├── .env.example                           # Example environment variables
├── .env                                   # Environment variables (not in git)
├── .gitignore                             # Git ignore rules
├── alembic.ini                            # Alembic configuration
├── docker-compose.yml                     # Docker Compose configuration
├── Dockerfile                             # Docker image definition
├── Makefile                               # Convenience commands
├── requirements.txt                       # Python dependencies
├── README.md                              # Project documentation
└── PROJECT_STRUCTURE.md                   # This file
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
DATABASE_URL=postgresql+asyncpg://postgres:postgres@db:5432/coffee_shop
REDIS_URL=redis://redis:6379/0
SECRET_KEY=your-super-secret-key-change-in-production
MAILJET_API_KEY=your-mailjet-api-key
MAILJET_API_SECRET=your-mailjet-api-secret
MAILJET_FROM_EMAIL=noreply@coffeeshop.com
```

4. **Start with Docker Compose**
```bash
docker-compose up -d
```

The API will be available at:
- **API**: http://localhost:8000
- **Swagger Docs**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

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

### Email sending (async)

This project uses Celery to send verification emails asynchronously. The `MailJetEmailService`
dispatches a Celery task instead of sending email synchronously so that HTTP responses stay fast.

How it works:
- In development mode (`ENVIRONMENT=development`) emails are printed to the console.
- In production, the `app.infrastructure.celery.email_tasks.send_verification_email` task
  sends the email via MailJet.

To process queued email tasks make sure Redis (or your configured broker) is running and then start a worker:

```bash
celery -A app.infrastructure.celery.worker worker --loglevel=info
```

If you want periodic jobs (like cleanup) enabled, also start beat in a separate terminal:

```bash
celery -A app.infrastructure.celery.worker beat --loglevel=info
```

Notes & next steps:
- Consider adding retries, timeouts and monitoring for the email task.
- For high volume, consider dedicated worker queues and rate limits for the MailJet API.


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
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

#### POST /auth/verify
Verify email address.

**Request Body:**
```json
{
  "email": "user@example.com",
  "verification_code": "abc123xyz..."
}
```

**Response:** `200 OK`
```
