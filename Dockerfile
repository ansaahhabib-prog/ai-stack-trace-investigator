FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install some basic tools that might be needed for debugging
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Command to run when starting the container (usually overridden)
CMD ["python", "--version"]
