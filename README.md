# Wakala Connect

Location-based marketplace connecting Master Agents and Minor Agents in Tanzania's mobile-money ecosystem.

## Local Setup (without Docker)

1. **Create and activate a virtual environment**

   ```bash
   python -m venv .venv
   # Windows
   .venv\Scripts\activate
   # Linux/macOS
   source .venv/bin/activate
   ```

2. **Install requirements**

   ```bash
   pip install -r requirements/development.txt
   ```

3. **Configure environment variables**

   ```bash
   cp .env.example .env
   # Edit .env with your local settings
   # For local (non-Docker) dev, override DATABASE_URL and REDIS_URL to point at localhost:
   #   DATABASE_URL=postgres://wakala:wakala@localhost:5432/wakala_connect
   #   REDIS_URL=redis://localhost:6379/0
   ```

4. **Run migrations**

   ```bash
   python manage.py migrate
   ```

5. **Run the development server**

   ```bash
   python manage.py runserver
   ```

## Run with Docker

Prerequisites: Docker and Docker Compose (v2) installed on your machine.

1. **Configure environment variables**

   ```bash
   cp .env.example .env
   ```

   The defaults in `.env.example` already point `DATABASE_URL` and `REDIS_URL` at the Docker
   service names (`db`, `redis`), so no changes are needed for Docker usage.

2. **Build and start all services**

   ```bash
   docker compose up --build
   ```

   This starts three containers:
   - `db` — PostGIS 16 (PostgreSQL with spatial extensions)
   - `redis` — Redis 7 (cache, Celery broker)
   - `web` — Django development server with hot-reload

3. **Run migrations** (in a second terminal)

   ```bash
   docker compose exec web python manage.py migrate
   ```

4. **Open the app**

   Visit [http://localhost:8000](http://localhost:8000) in your browser.

5. **Stop all services**

   ```bash
   docker compose down
   ```

   To also remove the database volume (⚠️ deletes all data):

   ```bash
   docker compose down -v
   ```
