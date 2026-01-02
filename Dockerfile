# ====================================
# 🐳 Production Dockerfile for Django
# ====================================

# Use an official Python runtime as a parent image
FROM python:3.10-slim-bullseye

# Set environment variables
# PYTHONDONTWRITEBYTECODE: Prevents Python from writing pyc files to disc
# PYTHONUNBUFFERED: Prevents Python from buffering stdout and stderr
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Set work directory
WORKDIR /app

# Install system dependencies
# libpq-dev: for psycopg2 (PostgreSQL)
# build-essential: for compiling Python packages
# gettext: for Django translations
# netcat: for waiting for DB
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    gettext \
    netcat \
    && rm -rf /var/lib/apt/lists/*

# Create a non-root user
RUN addgroup --system django && adduser --system --group django

# Install dependencies
COPY requirements.txt .
RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install gunicorn

# Copy project
COPY . .

# Create directory for static files and set permissions
RUN mkdir -p /app/staticfiles /app/media /app/logs \
    && chown -R django:django /app

# Switch to non-root user
USER django

# Entrypoint script to handle database connection waiting and migrations
COPY --chown=django:django ./entrypoint.sh /app/entrypoint.sh
RUN chmod +x /app/entrypoint.sh

ENTRYPOINT ["/app/entrypoint.sh"]
