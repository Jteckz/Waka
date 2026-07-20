# Wakala Connect — Project Documentation

## What Has Been Implemented (Phases 1–5)

### Phase 1: Project Scaffolding
- Django project with `config/` package (settings split into `base.py`, `development.py`, `testing.py`, `production.py`)
- PostgreSQL via `dj-database-url`, Redis cache/ Celery broker
- DRF + `djangorestframework-simplejwt` for API/auth
- `django-cors-headers`, `drf-spectacular` (OpenAPI), `django-filter`, `django-fsm`, `django-simple-history`, `structlog`, `sentry-sdk`
- `common/` library app with `BaseModel` (UUID pk + timestamps), `constants.py`, `exceptions.py`, `mixins.py`, `pagination.py`, `permissions.py`, `utils.py`, `validators.py`

### Phase 2: Common App Utilities
- `BaseModel` (UUID pk + `created_at`/`updated_at`), `TimestampedMixin`, `SoftDeleteMixin`
- `RoleChoices` (MASTER_AGENT, MINOR_AGENT, ADMIN) + `RequestStatusChoices`
- `DomainError` hierarchy + DRF custom exception handler
- `IsOwnerOrReadOnly` object-level permission
- `validate_image_file()` with MIME + size checks
- `StandardCursorPagination` + `StandardPageNumberPagination`
- `SoftDeleteQuerySetMixin` with `all_with_deleted()`
- `uuid_slugify()` helper

### Phase 3: Foundation Tests
- 40+ tests covering common app utilities, settings, pagination, exceptions, permissions

### Phase 4: Accounts App
- `apps/accounts/models.py`: Custom `User(AbstractUser)` with `phone` as `USERNAME_FIELD`, `role` field (RoleChoices), keeps integer PK (documented)
- `apps/accounts/managers.py`: `UserManager` with `create_user(phone, ...)` and `create_superuser`
- `apps/accounts/services.py`: `register_user()` — validates role (rejects ADMIN), duplicate phone, password policy
- `apps/accounts/validators.py`: `LetterDigitPasswordValidator` (requires letter + digit)
- `apps/accounts/admin.py`: `UserAdmin` with phone/role in list display
- **API endpoints** (`/api/v1/auth/`):
  - `POST /register` — creates user + returns JWT pair
  - `POST /login` — phone-based JWT obtain
  - `POST /login/refresh` — refresh token
  - `GET /me` — authenticated user profile
- JWT: 15-min access + 1-day refresh with rotation + blacklisting
- Tests: 3 test modules covering models, services, API (27 tests)

### Phase 5: RBAC Hardening
- `common/permissions.py`: `IsMasterAgent`, `IsMinorAgent`, `IsAdminRole` + existing `IsOwnerOrReadOnly`
- `apps/accounts/tests/factories.py`: `UserFactory` with role parameter + traits (`master`, `minor`, `admin`)
- `common/tests/test_permissions.py`: Rewritten — parametrized tests with real `User` instances via `UserFactory` + `APIRequestFactory` + inline test views
- `docs/architecture.md`: RBAC matrix documented

### Phase 6 (Current): Networks App
- `apps/networks/models.py`: `Network(BaseModel)` with `name` (unique, indexed), `logo` (URLField, blank), `network_type` (TextChoices: TELECOM/BANK), `is_active` (default True)
  - **URLField chosen over ImageField** for MVP simplicity — avoids file upload, storage, and serving complexity
- Seed data migration (`0002_seed_networks.py`) — creates exactly 7 networks via `RunPython`:
  - **Telecom:** Airtel, Vodacom, Yas/Tigo, Halotel
  - **Bank:** CRDB, NMB, NBC
- `apps/networks/admin.py`: Registered with `list_display=(name, network_type, is_active)`, `list_filter=network_type`
- **API endpoint** (`GET /api/v1/networks/`):
  - Public (`AllowAny`), read-only `ListAPIView`
  - Filtered to `is_active=True` by default
  - Cached for 15 minutes via `@cache_page`
- Tests: 2 test modules covering models (str, uniqueness) and API (7 seeded networks, correct fields, no-auth, inactive filtering)

### Total Test Count: **75 tests** — all passing

---

## How to Run the Project

### Prerequisites
- Python 3.12+
- PostgreSQL (for development) or SQLite (for testing)
- Redis (for caching + Celery — optional for local dev)
- Docker (optional, for containerized setup)

### Local Setup (No Docker)

```bash
# 1. Clone & enter the project
git clone <repo-url> wakala-connect
cd wakala-connect

# 2. Create virtual environment
python -m venv .venv
.venv\Scripts\activate     # Windows
# source .venv/bin/activate  # Linux/Mac

# 3. Install dependencies
pip install -r requirements/development.txt
pip install -r requirements/testing.txt

# 4. Configure environment
cp .env.example .env
# Edit .env — at minimum set DJANGO_SECRET_KEY and DATABASE_URL

# 5. Apply migrations
python manage.py migrate

# 6. Run the development server
python manage.py runserver

# 7. Visit http://localhost:8000
```

### Docker Setup

```bash
# 1. Build and start containers
docker-compose up --build

# 2. Apply migrations
docker-compose exec web python manage.py migrate

# 3. Visit http://localhost:8000
```

The `docker-compose.yml` includes:
- `web` — Django application (gunicorn)
- `db` — PostgreSQL
- `redis` — Redis cache/broker
- `celery_worker` — Celery worker

---

## How to Run Tests

### All Tests

```bash
# Using pytest directly
python -m pytest

# With verbose output
python -m pytest -v

# With short traceback (cleaner failures)
python -m pytest --tb=short

# Quiet mode (just pass/fail counts)
python -m pytest -q
```

### Run Tests by App

```bash
# Common app tests
python -m pytest common/tests/

# Accounts app tests
python -m pytest apps/accounts/tests/

# Networks app tests
python -m pytest apps/networks/tests/

# Settings/environment tests
python -m pytest tests/
```

### Run Specific Test Files

```bash
python -m pytest apps/networks/tests/test_api.py
python -m pytest common/tests/test_permissions.py
```

### Run Specific Tests

```bash
# By test class
python -m pytest apps/accounts/tests/test_api.py::TestRegister

# By individual test
python -m pytest apps/networks/tests/test_api.py::TestNetworkList::test_returns_all_seeded_networks
```

### Run Linter

```bash
python -m ruff check .
```

---

## API Endpoints

| Method | Endpoint                    | Auth Required | Description                        |
|--------|-----------------------------|---------------|------------------------------------|
| POST   | `/api/v1/auth/register`     | No            | Register new user (phone, password)|
| POST   | `/api/v1/auth/login`        | No            | Obtain JWT access + refresh tokens |
| POST   | `/api/v1/auth/login/refresh`| No            | Refresh an expired access token    |
| GET    | `/api/v1/auth/me`           | Yes           | Current authenticated user profile |
| GET    | `/api/v1/networks/`         | No (public)   | List active networks (cached 15m)  |
| GET    | `/admin/`                   | Admin         | Django admin interface             |

### Example: Register a user

```bash
curl -X POST http://localhost:8000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{"phone": "+255712000001", "password": "mypass123", "role": "MASTER_AGENT"}'
```

### Example: Login

```bash
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"phone": "+255712000001", "password": "mypass123"}'
```

### Example: List networks (public)

```bash
curl http://localhost:8000/api/v1/networks/
```

---

## Project Structure

```
wakala-connect/
├── api/
│   └── v1/
│       └── urls.py              # Top-level API v1 URL routing
├── apps/
│   ├── accounts/
│   │   ├── api/v1/views.py, serializers.py, urls.py
│   │   ├── migrations/
│   │   ├── tests/
│   │   │   ├── factories.py     # UserFactory (reusable by all apps)
│   │   │   ├── test_api.py
│   │   │   ├── test_models.py
│   │   │   └── test_services.py
│   │   ├── admin.py
│   │   ├── apps.py
│   │   ├── managers.py
│   │   ├── models.py
│   │   ├── services.py
│   │   └── validators.py
│   └── networks/
│       ├── api/v1/views.py, serializers.py, urls.py
│       ├── migrations/
│       │   ├── 0001_initial.py
│       │   └── 0002_seed_networks.py  # Seeds 7 networks
│       ├── tests/
│       │   ├── test_models.py
│       │   └── test_api.py
│       ├── admin.py
│       ├── apps.py
│       └── models.py
├── common/
│   ├── tests/
│   │   ├── test_exceptions.py
│   │   ├── test_pagination.py
│   │   └── test_permissions.py
│   ├── constants.py
│   ├── exceptions.py
│   ├── mixins.py
│   ├── models.py              # BaseModel, TimestampedMixin, etc.
│   ├── pagination.py
│   ├── permissions.py          # IsMasterAgent, IsMinorAgent, IsAdminRole, IsOwnerOrReadOnly
│   ├── utils.py
│   └── validators.py
├── config/
│   ├── settings/
│   │   ├── base.py
│   │   ├── development.py
│   │   ├── testing.py
│   │   └── production.py
│   └── urls.py
├── docs/
│   └── architecture.md         # RBAC matrix
├── requirements/
│   ├── base.txt
│   ├── development.txt
│   ├── production.txt
│   └── testing.txt
├── tests/
│   └── test_settings.py
├── docker-compose.yml
├── manage.py
├── pyproject.toml
└── my_test1.md                 # This file
```

---

## Key Design Decisions

1. **Integer PK on User model** — `AbstractUser` is tightly coupled to integer PKs across Django's auth infrastructure; switching to UUID would require extensive patching with no practical benefit at current scale.

2. **URLField for network logo** — Avoids file upload, storage configuration, and serving complexity for MVP. Can be upgraded to ImageField when file uploads are required.

3. **Seed data via migration (RunPython)** — More reliable than raw fixture files; executes within the migration transaction and has a reversible function.

4. **Public networks endpoint** — Network reference data is intentionally public (no auth required). Cached for 15 minutes via `@cache_page` decorator.
