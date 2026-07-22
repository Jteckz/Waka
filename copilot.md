# Wakala Connect — Project Status Summary

This document gives a practical overview of the project as it stands today, including the main features that have been implemented and how to test them.

## 1. What the project is about

Wakala Connect is a Django REST API project for connecting:
- Master Agents
- Minor Agents
- Networks (telecom and bank providers)

The product is built around location-based discovery, agent profiles, and network membership/status management for Tanzania’s mobile-money ecosystem.

## 2. Core architecture

The project is organized into logical Django apps:

- accounts: authentication, user management, role-based access
- agents: master/minor agent profiles, network statuses, nearby-agent discovery
- geo: reusable geolocation helpers and distance calculations
- networks: seedable network reference data
- common: shared utilities, exceptions, permissions, pagination, and base models

The API layer is exposed under:
- /api/v1/auth/
- /api/v1/networks/
- /api/v1/agents/

## 3. Implemented features

### 3.1 Authentication and user accounts
Implemented:
- Custom user model using phone as the login identifier
- Role-based users: MASTER_AGENT, MINOR_AGENT, and ADMIN
- Registration endpoint
- Login endpoint
- Token refresh endpoint
- Authenticated profile endpoint
- Password validation during registration
- Duplicate phone handling

What this covers:
- New users can be created with a phone number and password
- Login is based on phone and password
- JWT-based authentication is available
- Authenticated users can fetch their own profile

### 3.2 Role-based access control
Implemented:
- Permission classes for master agents, minor agents, and admins
- Profile access rules based on user role
- Owner-based read/write rules for profiles

This means:
- Master agents can manage master-profile resources
- Minor agents can manage minor-profile resources
- Admin-level access is reserved for admin users

### 3.3 Networks module
Implemented:
- Network model with name, logo, network type, and active flag
- Seeded network data for major telecom and bank providers
- Public list API for active networks
- Cached network list endpoint

Included network types:
- TELECOM
- BANK

### 3.4 Geolocation support
Implemented:
- Latitude/longitude validation
- Distance calculation between coordinates
- Radius filtering logic
- Nearby-location query support for agent discovery

This is a reusable internal capability used by the agents module.

### 3.5 Agents module
Implemented:
- Master agent profile model
- Minor agent profile model
- Network status model for master agents
- Profile creation services
- Location update logic
- Active/inactive status handling
- Network status management
- Nearby master-agent search based on coordinates and filter parameters
- Profile endpoints for both master and minor agents

This is the main business logic of the system.

### 3.6 API endpoints available
Current API routes include:

Auth:
- POST /api/v1/auth/register
- POST /api/v1/auth/login
- POST /api/v1/auth/login/refresh
- GET /api/v1/auth/me

Networks:
- GET /api/v1/networks/

Agents:
- GET /api/v1/agents/master/me
- PATCH /api/v1/agents/master/me
- GET /api/v1/agents/minor/me
- PATCH /api/v1/agents/minor/me
- GET /api/v1/agents/master/network-status
- POST /api/v1/agents/master/network-status
- GET /api/v1/agents/master/nearby
- GET /api/v1/agents/master/<uuid:pk>

## 4. Testing strategy

The project already contains a structured test suite covering the main domain areas.

### 4.1 Test areas included
- Accounts: user model, registration, login, services, API behavior
- Agents: profile creation, profile permissions, network status, selector behavior
- Geo: coordinate validation and proximity calculations
- Networks: model behavior and public API behavior
- Common: permissions, pagination, exceptions, utilities

### 4.2 How to run the tests

From the project root:

```bash
python -m pytest
```

Or run by area:

```bash
python -m pytest common/tests/
python -m pytest apps/accounts/tests/
python -m pytest apps/networks/tests/
python -m pytest apps/geo/tests/
python -m pytest apps/agents/tests/
```

For a specific file:

```bash
python -m pytest apps/agents/tests/test_api.py
python -m pytest apps/geo/tests/test_services.py
```

### 4.3 What to test manually

#### Register a user
```bash
curl -X POST http://localhost:8000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{"phone": "+255712000001", "password": "mypass123", "role": "MASTER_AGENT"}'
```

#### Login
```bash
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"phone": "+255712000001", "password": "mypass123"}'
```

#### Get the authenticated profile
```bash
curl -H "Authorization: Bearer <access_token>" \
  http://localhost:8000/api/v1/auth/me
```

#### List networks
```bash
curl http://localhost:8000/api/v1/networks/
```

#### Get own master profile
```bash
curl -H "Authorization: Bearer <access_token>" \
  http://localhost:8000/api/v1/agents/master/me
```

#### Find nearby master agents
```bash
curl -H "Authorization: Bearer <access_token>" \
  "http://localhost:8000/api/v1/agents/master/nearby?lat=-6.8&lng=39.2&radius_km=10"
```

## 5. How to run the project locally

### Option 1: Local virtual environment
```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements/development.txt
python manage.py migrate
python manage.py runserver
```

### Option 2: Docker
```bash
docker compose up --build
docker compose exec web python manage.py migrate
```

## 6. Current project status

The project has reached a solid MVP stage with:
- working authentication flow
- role-based API access
- agent profile management
- network reference data
- geolocation and proximity logic
- test coverage across the main app modules

It is now in a good position for further expansion, such as:
- richer agent onboarding flows
- more advanced search and matching
- transaction or request lifecycle features
- production hardening and deployment tuning
