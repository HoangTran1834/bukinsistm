# Dockerfile for Django backend
FROM python:3.12-slim

WORKDIR /app

# Cài các thư viện hệ thống cần thiết cho mysqlclient và build
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        build-essential \
        default-libmysqlclient-dev \
        pkg-config \
        python3-dev \
        default-mysql-client \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements và cài sớm để cache
COPY requirements.txt ./
RUN python -m venv /app/venv \
    && . /app/venv/bin/activate \
    && pip install --upgrade pip \
    && pip install -r requirements.txt

# Copy rest of backend code
COPY . .

# Entrypoint script will handle DB import, migrate, runserver, etc.
ENTRYPOINT ["sh", "/app/entrypoint.sh"]
