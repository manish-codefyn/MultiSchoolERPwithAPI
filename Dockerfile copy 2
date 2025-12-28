# Pull base image
FROM python:3.10.4-slim-bullseye

# Set environment variables
ENV PIP_DISABLE_PIP_VERSION_CHECK 1
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Set work directory
WORKDIR /app

# Install dependencies
COPY ./requirements.txt .
RUN pip install -r requirements.txt

# Copy project files into the container
COPY . .

# Install Gunicorn for running the app in production
RUN pip install gunicorn

# Expose port 9700 (default for Gunicorn)
EXPOSE 8700

# Command to run Gunicorn as the WSGI server
CMD ["gunicorn", "--bind", "0.0.0.0:8700", "config.wsgi:application"]
