# Use Python 3.12 slim base image
FROM python:3.12-slim

# Set working directory
WORKDIR /application

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    python3-dev \
    libffi-dev \
    libssl-dev \
    curl \
    git \
    bash \
    llvm-dev \
    && rm -rf /var/lib/apt/lists/*

# Upgrade pip and install uv
RUN python3 -m pip install --upgrade pip \
    && pip install uv

# Copy only dependency files first for caching
# COPY pyproject.toml uv.lock* ./
COPY . .

# Install dependencies with uv (system install, no venv)
# RUN uv pip install --system --requirement pyproject.toml

# Copy the rest of the application
# COPY . .

# # Expose default port (adjust if needed)
# EXPOSE 8000

# # Default command
# CMD ["tail", "-f", "/dev/null"]
