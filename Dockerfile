# Use an official Python runtime as a parent image
FROM python:3.9-slim

# Set the working directory in the container
WORKDIR /app

# Copy dependency checker script
COPY scripts/install_dependencies.sh /tmp/install_dependencies.sh
RUN chmod +x /tmp/install_dependencies.sh

# Install build dependencies required for pybullet and other packages
# The script checks for missing dependencies and provides helpful suggestions
RUN apt-get update && apt-get install -y build-essential && rm -rf /var/lib/apt/lists/*

# Copy the requirements file and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code
COPY . .

# Expose the port the app runs on
EXPOSE 8000

# Command to run the API
CMD ["uvicorn", "optimizer.api.main:app", "--host", "0.0.0.0", "--port", "8000"]