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

# Copy your project code
COPY . .

# Entrypoint
CMD ["python", "etl_main.py"]
