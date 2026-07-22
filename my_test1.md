# Wakala Connect — Project Documentation

## What Has Been Implemented (Phases 1–8)

### Phase 1: Project Scaffolding
- Django project with `config/` package (settings split into `base.py`, `development.py`, `testing.py`, `production.py`)
- PostgreSQL via `dj-database-url`, Redis cache / Celery broker
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
- Tests: 3 test modules covering models, services, API

### Phase 5: RBAC Hardening
- `common/permissions.py`:
  - `IsMasterAgent` / `IsMinorAgent` — compare against `RoleChoices` enum values directly (no longer duck-typed)
  - `IsAdminRole` added — checks `role == RoleChoices.ADMIN`
  - `IsOwnerOrReadOnly` — unchanged object-level permission
- `apps/accounts/tests/factories.py`: `UserFactory` (factory_boy `DjangoModelFactory`)
  - Uses `create_user()` via custom `_create` override
  - `phone` via `Sequence`, `password` via `make_password`, `role` as explicit parameter
  - Traits: `.master` (MASTER_AGENT), `.minor` (MINOR_AGENT), `.admin` (ADMIN)
  - No accounts-specific coupling — importable by any future app's tests
- `common/tests/test_permissions.py`: Rewritten from mocks to real `User` instances
  - Parametrized test covering all 9 `{IsMasterAgent, IsMinorAgent, IsAdminRole} × {MASTER_AGENT, MINOR_AGENT, ADMIN}` combinations
  - Uses `APIRequestFactory` + `force_authenticate` + inline `_ProtectedView`
- `docs/architecture.md`: RBAC matrix table with (endpoint category × role)

### Phase 6: Networks App
- `apps/networks/models.py`: `Network(BaseModel)` with `name` (unique, indexed), `logo` (URLField, blank), `network_type` (TELECOM/BANK), `is_active` (default True)
  - **URLField chosen over ImageField** for MVP simplicity
- Seed data migration (`0002_seed_networks.py`) — creates exactly 7 networks via `RunPython`:
  - **Telecom:** Airtel, Vodacom, Yas/Tigo, Halotel
  - **Bank:** CRDB, NMB, NBC
- `apps/networks/admin.py`: Registered with `list_display=(name, network_type, is_active)`, `list_filter=network_type`
- **API endpoint** (`GET /api/v1/networks/`):
  - Public (`AllowAny`), read-only `ListAPIView`
  - Filtered to `is_active=True` by default
  - Cached for 15 minutes via `@cache_page`
- Tests: 2 test modules covering models (str, uniqueness) and API (7 seeded networks, correct fields, no-auth, inactive filtering)

### Phase 7: Geo App (Internal Geolocation)
- `apps/geo/models.py`: `GeoLocatedModel` — abstract model with `latitude`/`longitude` FloatFields + `set_coordinates(lat, lng)` method
  - **FloatField chosen over PointField** since GDAL is not available on all dev environments; production can migrate to PostGIS PointField
- `apps/geo/utils.py`: `validate_latitude()` and `validate_longitude()` with range validation
- `apps/geo/services.py`: Pure-Python distance calculations via `geopy`
  - `calculate_distance_km(point_a, point_b) -> float`
  - `is_within_radius(point_a, point_b, radius_km) -> bool`
  - `validate_within_service_radius(origin, target, radius_km)` — raises `OutOfServiceRadiusError`
- `apps/geo/selectors.py`: `nearby(queryset, point, radius_km) -> QuerySet`
  - Uses haversine formula via Django ORM expressions (works on SQLite and PostgreSQL)
  - Annotates `distance` in km, filters within radius, orders ascending
- **No API endpoints** — pure internal capability consumed by other apps
- Tests: coordinate validation, known-distance checks (Dar es Salaam ~4.2km), radius bounds, nearby filtering/ordering

### Phase 8: Agents App (Business Logic)
- **Models**:
  - `MasterAgentProfile(BaseModel, GeoLocatedModel)`: OneToOne to User (PROTECT), `business_name` (indexed), `profile_photo` (URLField), `business_photos` (JSONField), `is_active` (indexed), `response_rate` (nullable Decimal)
  - `MinorAgentProfile(BaseModel)`: OneToOne to User (PROTECT), `display_name` (optional)
  - `AgentNetworkStatus(BaseModel)`: FK to MasterAgentProfile (CASCADE), FK to Network (PROTECT), `is_active` (indexed). UniqueConstraint on (master_agent, network)
- **Services**:
  - `create_master_agent_profile(user, business_name)` — validates user.role == MASTER_AGENT
  - `create_minor_agent_profile(user)` — validates user.role == MINOR_AGENT
  - `update_master_agent_location(profile, lat, lng)` — uses geo validation + `set_coordinates`
  - `set_agent_active_status(profile, is_active)`
  - `set_network_status(profile, network, is_active)` — get_or_create pattern
- **Signal**: `post_save` on User auto-creates the appropriate profile on registration (chosen over service-call approach to avoid circular import between accounts and agents)
- **Selectors**: `get_master_agent_profile(user)`, `get_minor_agent_profile(user)`, `list_network_statuses(profile)`
- **API endpoints** (`/api/v1/agents/`):
  - `GET /master/me` — own master profile (IsMasterAgent)
  - `PATCH /master/me` — update business_name, profile_photo, etc.
  - `GET /minor/me` — own minor profile (IsMinorAgent)
  - `PATCH /minor/me` — update display_name
  - `GET /master/network-status` — list network statuses
  - `POST /master/network-status` — create/update network status
- Tests: uniqueness constraints, PROTECT on delete, role validation, coordinate storage, signal-based auto-creation, API permission checks

### Total Test Count: **113 tests** — all passing

---

## API Endpoints — Complete Reference

| Method | Endpoint                              | Auth Required | Permission        | Description                               |
|--------|---------------------------------------|---------------|-------------------|-------------------------------------------|
| POST   | `/api/v1/auth/register`               | No            | —                 | Register new user (phone, password)       |
| POST   | `/api/v1/auth/login`                  | No            | —                 | Obtain JWT access + refresh tokens        |
| POST   | `/api/v1/auth/login/refresh`          | No            | —                 | Refresh an expired access token           |
| GET    | `/api/v1/auth/me`                     | Yes           | IsAuthenticated   | Current authenticated user profile        |
| GET    | `/api/v1/networks/`                   | No (public)   | AllowAny          | List active networks (cached 15m)         |
| GET    | `/api/v1/agents/master/me`            | Yes           | IsMasterAgent     | Own master agent profile                  |
| PATCH  | `/api/v1/agents/master/me`            | Yes           | IsMasterAgent     | Update master agent profile               |
| GET    | `/api/v1/agents/minor/me`             | Yes           | IsMinorAgent      | Own minor agent profile                   |
| PATCH  | `/api/v1/agents/minor/me`             | Yes           | IsMinorAgent      | Update minor agent profile                |
| GET    | `/api/v1/agents/master/network-status`| Yes           | IsMasterAgent     | List network statuses                     |
| POST   | `/api/v1/agents/master/network-status`| Yes           | IsMasterAgent     | Create/update network status              |
| GET    | `/admin/`                             | Admin         | Admin user        | Django admin interface                    |

### Quick-Start Examples

```bash
# Register a master agent
curl -X POST http://localhost:8000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{"phone": "+255712000001", "password": "mypass123", "role": "MASTER_AGENT"}'

# Login
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"phone": "+255712000001", "password": "mypass123"}'

# Use the returned access_token in subsequent requests:
TOKEN="<access_token>"

# Get master profile
curl -H "Authorization: Bearer $TOKEN" http://localhost:8000/api/v1/agents/master/me

# Update business name
curl -X PATCH http://localhost:8000/api/v1/agents/master/me \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"business_name": "My Shop"}'

# Toggle network status (requires a seeded network UUID)
curl -X POST http://localhost:8000/api/v1/agents/master/network-status \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"network_id": "<network-uuid>", "is_active": true}'

# List networks (public)
curl http://localhost:8000/api/v1/networks/
```

---

## How to Run Tests

```bash
# All tests (113 total)
python -m pytest

# By app
python -m pytest common/tests/
python -m pytest apps/accounts/tests/
python -m pytest apps/networks/tests/
python -m pytest apps/geo/tests/
python -m pytest apps/agents/tests/

# Specific test files
python -m pytest apps/agents/tests/test_api.py
python -m pytest apps/geo/tests/test_services.py
python -m pytest apps/agents/tests/test_signals_or_wiring.py

# With short traceback (cleaner failures)
python -m pytest --tb=short

# Linter
python -m ruff check .
```

---

## Project Structure

```
wakala-connect/
├── api/v1/urls.py              # Top-level API routing
├── apps/
│   ├── accounts/               # Auth & user management (Phase 4)
│   ├── agents/                 # Business profiles & network status (Phase 8)
│   │   ├── api/v1/             # Serializers, views, urls
│   │   ├── admin.py            # All 3 models registered
│   │   ├── apps.py             # AppConfig + signal registration
│   │   ├── models.py           # MasterAgentProfile, MinorAgentProfile, AgentNetworkStatus
│   │   ├── selectors.py        # Profile/status retrieval
│   │   ├── services.py         # Profile creation, location, network status
│   │   ├── signals.py          # Auto-create profile on User post_save
│   │   └── tests/
│   ├── geo/                    # Internal geolocation (Phase 7)
│   │   ├── models.py           # GeoLocatedModel (abstract)
│   │   ├── services.py         # Distance calculations via geopy
│   │   ├── selectors.py        # nearby() queryset helper (haversine)
│   │   ├── utils.py            # Coordinate validation
│   │   └── tests/
│   └── networks/               # Reference data (Phase 6)
├── common/                     # Shared utils, models, permissions
├── config/                     # Django settings (base/development/testing/production)
├── docs/architecture.md        # RBAC matrix
├── requirements/
├── tests/                      # Environment/settings tests
├── docker-compose.yml
└── manage.py
```

---

## Key Design Decisions

1. **Integer PK on User** — `AbstractUser` is tightly coupled to integer PKs across Django's auth infrastructure; switching to UUID would require extensive patching with no practical benefit at current scale.

2. **URLField for media** — Profile photos and network logos use URLField instead of ImageField to avoid file upload, storage configuration, and serving complexity for MVP.

3. **Seed data via migration (RunPython)** — More reliable than raw fixture files; executes within the migration transaction and has a reversible function.

4. **FloatField for coordinates (not PointField)** — GDAL is not guaranteed in all environments (CI, local dev). The FloatField + geopy approach works everywhere; production with PostGIS can add a computed Point column.

5. **geopy for distance calculations** — Pure Python, no database dependency, testable in isolation.

6. **Signal-based profile auto-creation** — `post_save` on User creates the appropriate `MasterAgentProfile` or `MinorAgentProfile`. A direct service call from `accounts.services.register_user` was avoided because accounts is more foundational than agents (would create circular import). The tradeoff is documented in a code comment.

7. **Haversine via ORM expressions** — The `nearby()` selector implements the haversine formula using Django's `Sin`, `Cos`, `ASin`, `Sqrt` database functions, working on both SQLite and PostgreSQL without PostGIS-specific extensions.
