# Use lightweight Python base image
FROM python:3.11-slim-bookworm

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Create or set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    git \
    && rm -rf /var/lib/apt/lists/*

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy project files
COPY . .

# Expose port (Flask defaults to 5000, FastAPI defaults to 8000)
EXPOSE 5000

# Start the app (gunicorn recommended in prod)
CMD ["gunicorn", "-k", "eventlet", "-b", "0.0.0.0:5000", "app:app"]
