# Wakala Connect on Kali Linux

This guide helps you clone, set up, run, and work with the Wakala Connect project on Kali Linux.

The project is a Django REST API application that uses:
- Python
- PostgreSQL
- Redis
- Django REST Framework
- JWT authentication

## 1. Install base tools on Kali

Update the system first:

```bash
sudo apt update && sudo apt upgrade -y
```

Install the required packages:

```bash
sudo apt install -y git curl python3 python3-pip python3-venv build-essential libpq-dev postgresql postgresql-contrib redis-server redis-tools
```

If you want full geospatial support later, you can also install:

```bash
sudo apt install -y gdal-bin libgdal-dev python3-gdal
```

Start and enable the services:

```bash
sudo systemctl enable --now postgresql
sudo systemctl enable --now redis-server
```

Check that they are running:

```bash
sudo systemctl status postgresql redis-server
```

## 2. Clone the project

```bash
git clone <your-repo-url>
cd Wakala-connect
```

If you already have the repository, update it:

```bash
git pull
```

## 3. Create a Python virtual environment

```bash
python3 -m venv .venv
source .venv/bin/activate
```

Upgrade pip:

```bash
python -m pip install --upgrade pip setuptools wheel
```

## 4. Install Python dependencies

```bash
pip install -r requirements/development.txt
```

If installation fails because of system packages, make sure `build-essential` and `libpq-dev` are installed as shown above.

## 5. Set up PostgreSQL for the project

Switch to the PostgreSQL system user:

```bash
sudo -u postgres psql
```

Inside PostgreSQL, create a database and user:

```sql
CREATE USER wakala WITH PASSWORD 'wakala';
CREATE DATABASE wakala_connect OWNER wakala;
ALTER USER wakala CREATEDB;
\q
```

You can verify the database exists:

```bash
sudo -u postgres psql -l
```

## 6. Configure environment variables

Copy the example environment file:

```bash
cp .env.example .env
```

Open the file and edit it:

```bash
nano .env
```

Use values suitable for local Kali development. A good starting point is:

```env
DJANGO_SECRET_KEY=change-me-to-a-real-secret-key
DJANGO_DEBUG=True
DATABASE_URL=postgres://wakala:wakala@localhost:5432/wakala_connect
REDIS_URL=redis://localhost:6379/0
ALLOWED_HOSTS=localhost,127.0.0.1
CORS_ALLOWED_ORIGINS=http://localhost:5173,http://127.0.0.1:5173
SENTRY_DSN=
```

Important:
- Use `localhost` instead of `db` because you are not running the Docker containers.
- Keep `DJANGO_DEBUG=True` while developing locally.

## 7. Run database migrations

With the virtual environment active:

```bash
python manage.py migrate
```

If you get database connection errors, verify:
- PostgreSQL is running
- the database and user exist
- the `.env` file points to the right host and credentials

## 8. Create a superuser (optional but recommended)

```bash
python manage.py createsuperuser
```

Follow the prompts to create an admin account.

## 9. Run the development server

```bash
python manage.py runserver 0.0.0.0:8000
```

Open the app in your browser:

```text
http://127.0.0.1:8000
```

## 10. Run the test suite

Run all tests:

```bash
python -m pytest
```

Run tests by app:

```bash
python -m pytest common/tests/
python -m pytest apps/accounts/tests/
python -m pytest apps/networks/tests/
python -m pytest apps/geo/tests/
python -m pytest apps/agents/tests/
```

Run a specific test file:

```bash
python -m pytest apps/agents/tests/test_api.py
```

## 11. Useful development commands

Activate the environment:

```bash
source .venv/bin/activate
```

Deactivate it later:

```bash
deactivate
```

Check Django status:

```bash
python manage.py check
```

Start a Django shell:

```bash
python manage.py shell
```

## 12. Optional: run with Docker on Kali

If you prefer Docker instead of a local Python/PostgreSQL setup, install Docker first:

```bash
sudo apt install -y docker.io docker-compose-plugin
sudo systemctl enable --now docker
```

Then run:

```bash
docker compose up --build
```

In another terminal:

```bash
docker compose exec web python manage.py migrate
```

## 13. Common issues and fixes

### PostgreSQL authentication error

If you see authentication-related errors, verify the password and host in `.env`:

```env
DATABASE_URL=postgres://wakala:wakala@localhost:5432/wakala_connect
```

### Redis connection error

If Redis is not available, check:

```bash
redis-cli ping
```

Expected response:

```text
PONG
```

### Python package build errors

Install the missing system packages:

```bash
sudo apt install -y build-essential libpq-dev python3-dev
```

## 14. Recommended workflow for Kali

1. Update Kali
2. Install Python, PostgreSQL, Redis, and build tools
3. Create the PostgreSQL database/user
4. Create and activate the virtual environment
5. Install project dependencies
6. Set `.env` for local development
7. Run migrations
8. Start the server and test the API

This setup is enough to develop and test the project locally on Kali Linux.
