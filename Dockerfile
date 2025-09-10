# -------------------------
# Stage 1: Base image with Python and dependencies
# -------------------------
FROM python:3.12-slim AS base

WORKDIR /app

# Copy only requirements and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# -------------------------
# Stage 2: Project image
# -------------------------
FROM base AS project

WORKDIR /app

# Copy project files
COPY src/ src/
COPY config/ config/
COPY README.md README.md
COPY Dockerfile Dockerfile
COPY requirements.txt requirements.txt
COPY doc/ doc/

# Make src a package entry point
ENV PYTHONPATH=/app

# Run main.py as a module
CMD ["python", "-m", "src.main"]

