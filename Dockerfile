# Base image
FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Install system deps
RUN apt-get update && apt-get install -y \
    git \
    iputils-ping \
    dnsutils \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Install Poetry
RUN pip install poetry

# Copy only dependency files (cache optimization 🔥)
COPY pyproject.toml poetry.lock ./

# Install dependencies
RUN poetry config virtualenvs.create false \
    && poetry install --no-root

# Copy app
COPY . .

# Expose port
EXPOSE 8000

# Run app
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]