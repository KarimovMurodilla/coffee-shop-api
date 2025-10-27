# Architecture Documentation

## Clean Architecture Overview

This project implements **Clean Architecture** (also known as Onion Architecture or Hexagonal Architecture), which organizes code into layers with strict dependency rules.

### The Dependency Rule

**Source code dependencies must point only inward, toward higher-level policies.**

```
┌─────────────────────────────────────────────────────────────┐
│                    External Systems                          │
│  (Web, Database, Email Service, Cache, Background Tasks)    │
└─────────────────────┬───────────────────────────────────────┘
                      │
         ┌────────────▼────────────┐
         │    API Layer            │
         │  (Routes, Controllers)  │
         └────────────┬────────────┘
                      │
         ┌────────────▼────────────┐
         │  Infrastructure Layer   │
         │  (Implementations)      │
         └────────────┬────────────┘
                      │
         ┌────────────▼────────────┐
         │  Application Layer      │
         │  (Use Cases)            │
         └────────────┬────────────┘
                      │
         ┌────────────▼────────────┐
         │  Domain Layer           │
         │  (Business Logic)       │
         └─────────────────────────┘
```

## Layer Details

### 1. Domain Layer (Core Business Logic)

**Location**: `app/domain/`

**Purpose**: Contains the enterprise business rules and is completely independent of external frameworks.

**Contents**:
- **Entities** (`entities.py`): Core business objects
  - `User`: Represents a user with business logic methods
  - `UserRole`: Enum for user roles (USER, ADMIN)
  
- **Repository Interfaces** (`repositories.py`): 
  - `UserRepository`: Abstract interface for data access
  
- **Service Interfaces** (`services.py`):
  - `EmailService`: Abstract interface for email operations
  - `PasswordService`: Abstract interface for password operations
  - `TokenService`: Abstract interface for token operations

**Key Characteristics**:
- ✅ No external dependencies
- ✅ Pure Python classes
- ✅ Contains business rules and validations
- ✅ Framework-agnostic
- ✅ Testable without any infrastructure

**Example - User Entity**:
```python
class User:
    def is_admin(self) -> bool:
        return self.role == UserRole.ADMIN
    
    def can_verify(self, code: str) -> bool:
        # Business logic for verification
        ...
    
    def should_be_deleted(self) -> bool:
        # Business rule for cleanup
        ...
```

### 2. Application Layer (Use Cases)

**Location**: `app/application/`

**Purpose**: Orchestrates the flow of data to and from entities, implements application-specific business rules.

**Contents**:
- **DTOs** (`dto.py`): Data transfer objects for API communication
- **Exceptions** (`exceptions.py`): Application-specific exceptions
- **Use Cases** (`use_cases/`):
  - Authentication use cases (signup, login, verify, refresh)
  - User management use cases (CRUD operations, cleanup)

**Key Characteristics**:
- ✅ Depends only on Domain layer
- ✅ Contains application workflows
- ✅ Orchestrates domain objects
- ✅ Independent of frameworks and databases

**Example - Signup Use Case**:
```python
class SignupUseCase:
    def __init__(self, user_repo, password_service, email_service):
        self.user_repo = user_repo
        self.password_service = password_service
        self.email_service = email_service
    
    async def execute(self, request: SignupRequest) -> UserResponse:
        # 1. Check if user exists
        # 2. Hash password
        # 3. Create user entity
        # 4. Save to repository
        # 5. Send verification email
        ...
```

### 3. Infrastructure Layer (Technical Implementation)

**Location**: `app/infrastructure/`

**Purpose**: Implements the interfaces defined in the domain layer using specific technologies.

**Contents**:
- **Database** (`database/`):
  - SQLAlchemy models
  - Database connection setup
  
- **Repositories** (`repositories/`):
  - `SQLAlchemyUserRepository`: PostgreSQL implementation of UserRepository
  
- **Services** (`services/`):
  - `BcryptPasswordService`: bcrypt implementation
  - `JWTTokenService`: JWT implementation
  - `MailJetEmailService`: MailJet implementation
  
- **Background Tasks** (`celery/`):
  - Celery worker and periodic tasks

**Key Characteristics**:
- ✅ Implements domain interfaces
- ✅ Contains framework-specific code
- ✅ Handles external systems (DB, cache, email)
- ✅ Can be swapped without affecting business logic

**Example - User Repository**:
```python
class SQLAlchemyUserRepository(UserRepository):
    def __init__(self, session: AsyncSession):
        self.session = session
    
    async def create(self, user: User) -> User:
        # SQLAlchemy-specific implementation
        model = self._to_model(user)
        self.session.add(model)
        ...
```

### 4. API Layer (Interface Adapters)

**Location**: `app/api/`

**Purpose**: Adapts data from external format (HTTP) to internal format (use cases).

**Contents**:
- **Routes** (`routes/`):
  - `auth.py`: Authentication endpoints
  - `users.py`: User management endpoints
  
- **Dependencies** (`dependencies.py`):
  - Dependency injection configuration
  - Current user extraction from JWT

**Key Characteristics**:
- ✅ HTTP-specific code
- ✅ Request/response handling
- ✅ Dependency injection
- ✅ Error handling and status codes

**Example - Auth Route**:
```python
@router.post("/auth/signup")
async def signup(
    request: SignupRequest,
    user_repo=Depends(get_user_repository),
    password_service=Depends(get_password_service),
    email_service=Depends(get_email_service)
):
    use_case = SignupUseCase(user_repo, password_service, email_service)
    return await use_case.execute(request)
```

## System Architecture

### Component Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                         Client                               │
│                    (Web, Mobile, CLI)                        │
└────────────────────────┬────────────────────────────────────┘
                         │ HTTP/HTTPS
                         ▼
┌─────────────────────────────────────────────────────────────┐
│                      FastAPI Server                          │
│  ┌────────────┐  ┌────────────┐  ┌───────────────────────┐ │
│  │ Auth Routes│  │ User Routes│  │  Middleware (CORS,    │ │
│  │            │  │            │  │  Error Handling)      │ │
│  └─────┬──────┘  └─────┬──────┘  └───────────────────────┘ │
│        │                │                                    │
│        └────────┬───────┘                                    │
│                 │                                            │
│        ┌────────▼────────┐                                  │
│        │  Dependencies   │                                  │
│        │  (DI Container) │                                  │
│        └────────┬────────┘                                  │
└─────────────────┼────────────────────────────────────────────┘
                  │
    ┌─────────────┼─────────────┐
    │             │             │
    ▼             ▼             ▼
┌─────────┐ ┌──────────┐ ┌──────────┐
│  Use    │ │Password  │ │  Token   │
│  Cases  │ │ Service  │ │ Service  │
└────┬────┘ └──────────┘ └──────────┘
     │
     ▼
┌──────────────────┐
│   Repository     │
└────┬─────────────┘
     │
     ▼
┌─────────────────────────────────────────┐
│          PostgreSQL Database             │
│                                          │
│  ┌────────────────────────────────────┐ │
│  │          Users Table                │ │
│  │  - id                               │ │
│  │  - email                            │ │
│  │  - hashed_password                  │ │
│  │  - role                             │ │
│  │  - is_verified                      │ │
│  │  - verification_code                │ │
│  │  - timestamps                       │ │
│  └────────────────────────────────────┘ │
└─────────────────────────────────────────┘
```

### Async Task Processing

```
┌──────────────────┐
│   FastAPI API    │
│                  │
│  Signup User ───┼─────┐
│                  │     │
└──────────────────┘     │
                         │
                         │ Trigger Task
                         │
                         ▼
                  ┌──────────────┐
                  │    Redis     │
                  │    Queue     │
                  └──────┬───────┘
                         │
                         │ Task
                         │
                         ▼
                  ┌──────────────┐
                  │    Celery    │
                  │    Worker    │
                  │              │
                  │ - Send Email │
                  │ - Cleanup    │
                  └──────────────┘
```

### Data Flow: User Registration

```
1. Client sends POST /auth/signup
        │
        ▼
2. FastAPI receives request
        │
        ▼
3. Request validated by Pydantic (SignupRequest DTO)
        │
        ▼
4. Dependencies injected:
   - UserRepository
   - PasswordService
   - EmailService
        │
        ▼
5. SignupUseCase.execute() called
        │
        ├─► Check if email exists (UserRepository)
        │
        ├─► Hash password (PasswordService)
        │
        ├─► Create User entity (Domain object)
        │
        ├─► Generate verification code
        │
        ├─► Save to database (UserRepository.create())
        │       │
        │       ├─► Convert to SQLAlchemy model
        │       ├─► Insert into PostgreSQL
        │       └─► Return saved entity
        │
        ├─► Send verification email (EmailService)
        │       │
        │       └─► In dev: print to console
        │           In prod: call MailJet API
        │
        └─► Return UserResponse DTO
                │
                ▼
6. FastAPI serializes response to JSON
                │
                ▼
7. Client receives 201 Created with user data
```

## Security Architecture

### Authentication Flow

```
┌────────┐                                  ┌────────┐
│ Client │                                  │  API   │
└───┬────┘                                  └───┬────┘
    │                                           │
    │  1. POST /auth/login                     │
    │  {email, password}                       │
    ├──────────────────────────────────────────►
    │                                           │
    │                          2. Validate      │
    │                             credentials   │
    │                          3. Generate      │
    │                             JWT tokens    │
    │                                           │
    │  4. {access_token, refresh_token}        │
    ◄──────────────────────────────────────────┤
    │                                           │
    │  5. GET /users/me                        │
    │  Authorization: Bearer <access_token>    │
    ├──────────────────────────────────────────►
    │                                           │
    │                          6. Verify token  │
    │                          7. Get user      │
    │                                           │
    │  8. {user_data}                          │
    ◄──────────────────────────────────────────┤
    │                                           │
```

### Token Structure

**Access Token** (short-lived, 30 minutes):
```json
{
  "sub": "user_id",
  "exp": "expiration_timestamp",
  "type": "access"
}
```

**Refresh Token** (long-lived, 7 days):
```json
{
  "sub": "user_id",
  "exp": "expiration_timestamp",
  "type": "refresh"
}
```

### Authorization Layers

```
Request
    │
    ▼
┌───────────────────────┐
│  JWT Authentication   │  ← Verify token signature
│  (dependencies.py)    │  ← Check expiration
└──────────┬────────────┘  ← Extract user_id
           │
           ▼
┌───────────────────────┐
│  Get Current User     │  ← Load user from database
│  (dependencies.py)    │  ← Verify user exists
└──────────┬────────────┘
           │
           ▼
┌───────────────────────┐
│  Role Check           │  ← Admin-only endpoints
│  (use cases)          │  ← User can modify self
└──────────┬────────────┘
           │
           ▼
      Execute Use Case
```

## Database Schema

```sql
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    hashed_password VARCHAR(255) NOT NULL,
    first_name VARCHAR(100),
    last_name VARCHAR(100),
    role VARCHAR(20) NOT NULL DEFAULT 'user',
    is_verified BOOLEAN DEFAULT FALSE,
    verification_code VARCHAR(255),
    verification_code_expires_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX ix_users_email ON users(email);
CREATE INDEX ix_users_id ON users(id);
```

## Scalability Considerations

### Horizontal Scaling

The application is designed to scale horizontally:

1. **Stateless API**: No session data stored in memory
2. **JWT Tokens**: Self-contained, no server-side storage needed
3. **Async Operations**: Non-blocking I/O for better concurrency
4. **Separate Workers**: Celery workers can scale independently

```
            Load Balancer
                 │
     ┌───────────┼───────────┐
     │           │           │
     ▼           ▼           ▼
  API-1       API-2       API-3
     │           │           │
     └───────────┼───────────┘
                 │
        ┌────────┴────────┐
        │                 │
        ▼                 ▼
   PostgreSQL          Redis
   (Primary)          (Cache)
        │
        ▼
   PostgreSQL
   (Replicas)
```

### Caching Strategy (Future Enhancement)

```
Request
    │
    ▼
Check Redis Cache
    │
    ├─► Cache Hit ──► Return Cached Data
    │
    └─► Cache Miss
            │
            ▼
        Query Database
            │
            ▼
        Store in Cache
            │
            ▼
        Return Data
```

## Benefits of This Architecture

### 1. **Testability**
- Each layer can be tested independently
- Mock dependencies easily
- Fast unit tests (no database required)

### 2. **Maintainability**
- Clear separation of concerns
- Easy to understand and navigate
- Changes are localized

### 3. **Flexibility**
- Swap implementations without changing business logic
- Add new features without breaking existing code
- Support multiple clients (web, mobile, CLI)

### 4. **Independence**
- Business logic doesn't depend on frameworks
- Can change database without affecting use cases
- Can switch email providers easily

### 5. **Scalability**
- Async operations for better performance
- Stateless design for horizontal scaling
- Background tasks for heavy operations

## Trade-offs

### Advantages
✅ Clear structure and organization
✅ Highly testable
✅ Easy to maintain and extend
✅ Framework-independent business logic
✅ Great for complex domains

### Disadvantages
❌ More boilerplate code
❌ Steeper learning curve
❌ Might be overkill for simple CRUD apps
❌ More files and directories to navigate

## Conclusion

This architecture ensures:
- **Clean Code**: Easy to read and understand
- **SOLID Principles**: Each class has a single responsibility
- **DRY**: Don't repeat yourself
- **Separation of Concerns**: Each layer has a specific purpose
- **Production Ready**: Scalable, maintainable, and testable

Perfect for enterprise applications that need to grow and evolve over time!
