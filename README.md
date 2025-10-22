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
