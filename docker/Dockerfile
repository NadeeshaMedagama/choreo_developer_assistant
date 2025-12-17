# Multi-stage build for optimized image size
FROM python:3.11-slim as builder

# Set working directory
WORKDIR /app

# Install system dependencies for building Python packages
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    g++ \
    git \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements file (from nested directory)
COPY backend/choreo-ai-assistant/requirements.txt .

# Install Python dependencies using standard pip
RUN pip install --no-cache-dir --user -r requirements.txt

# Final stage
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install runtime dependencies only
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy Python packages from builder
COPY --from=builder /root/.local /root/.local

# Make sure scripts in .local are usable
ENV PATH=/root/.local/bin:$PATH

# Copy application code (backend is at root level, not in choreo-ai-assistant/)
COPY backend ./backend

# Set Python path
ENV PYTHONPATH=/app

# Set unbuffered output for Docker logs
ENV PYTHONUNBUFFERED=1

# Expose port if running as a service (optional)
EXPOSE 8000

# Default command - can be overridden
CMD ["python", "-m", "uvicorn", "backend.app:app", "--host", "0.0.0.0", "--port", "8000"]
