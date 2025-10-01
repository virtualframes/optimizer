# Stage 1: Builder - Installs dependencies
FROM python:3.9-slim AS builder

WORKDIR /app

# Install system-level build dependencies
RUN apt-get update && apt-get install -y build-essential && rm -rf /var/lib/apt/lists/*

# Copy and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application code and install it
COPY . .
RUN pip install -e .

# Stage 2: Runner - Creates the final, lean image
FROM python:3.9-slim

WORKDIR /app

# Copy installed dependencies from the builder stage
COPY --from=builder /usr/local/lib/python3.9/site-packages/ /usr/local/lib/python3.9/site-packages/
COPY --from=builder /usr/local/bin/ /usr/local/bin/

# Copy the application code
COPY . .

# Expose the API port
EXPOSE 8000

# Command to run the FastAPI application
CMD ["uvicorn", "optimizer.api.main:app", "--host", "0.0.0.0", "--port", "8000"]