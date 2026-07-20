# Stage 1 — builder: install system libs and Python deps
FROM python:3.12-slim AS builder

RUN apt-get update && apt-get install -y --no-install-recommends \
    binutils \
    gdal-bin \
    libpq-dev \
    libproj-dev \
    libgdal-dev \
    && rm -rf /var/lib/apt/lists/*

COPY requirements/ /build/requirements/
WORKDIR /build
RUN pip install --no-cache-dir -r requirements/production.txt

# Stage 2 — development: local dev with runserver
FROM builder AS development

RUN pip install --no-cache-dir django-extensions

WORKDIR /app

EXPOSE 8000

CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]

# Stage 3 — production: gunicorn
FROM builder AS production

WORKDIR /app

COPY . /app/

EXPOSE 8000

CMD ["gunicorn", "config.wsgi:application", "--bind", "0.0.0.0:8000", "--workers", "4"]
