# Architecture

## RBAC Matrix

Access control is enforced via `common/permissions.py` permission classes on views.
Unauthenticated requests are denied by `rest_framework`'s default `IsAuthenticated`
or by the role-checking classes themselves.

| Endpoint category          | Master Agent | Minor Agent | Admin |
|----------------------------|:------------:|:-----------:|:-----:|
| Auth (login, refresh)      |      ✓       |     ✓       |   ✓   |
| Registration               |     N/A      |    N/A      |   ✗   |
| Own profile (read)         |      ✓       |     ✓       |   ✓   |
| Own profile (write)        |      ✓       |     ✓       |   ✓   |
| Agent profiles (list/read) |      ✓       |     ✓       |   ✓   |
| Agent profiles (write)     |      ✓       |     ✗       |   ✓   |
| Admin-only actions         |      ✗       |     ✗       |   ✓   |

- **Auth endpoints** (`/api/v1/auth/login`, `/api/v1/auth/login/refresh`): accessible to
  any registered user regardless of role.
- **Registration** (`POST /api/v1/auth/register`): intentionally blocks the `ADMIN` role —
  admins are created via `createsuperuser` or the admin panel only.
- **Own profile** (read/write): any authenticated user, gated by `IsOwnerOrReadOnly`.
- **Agent profiles** (read): read-only access for all authenticated users.
- **Agent profiles** (write): only `MASTER_AGENT` and `ADMIN` can create/update/delete
  agent profiles. `MINOR_AGENT` users are read-only for all agent resources.
- **Admin-only actions**: reserved for `ADMIN` role behind `IsAdminRole`.

### Permission classes

| Class              | Grants access when user.role is     |
|--------------------|-------------------------------------|
| `IsMasterAgent`    | `MASTER_AGENT`                      |
| `IsMinorAgent`     | `MINOR_AGENT`                      |
| `IsAdminRole`      | `ADMIN`                             |
| `IsOwnerOrReadOnly`| object-level; read: anyone, write: owner |
