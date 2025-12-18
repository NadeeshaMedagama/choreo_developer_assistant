FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    gcc \
    g++ \
    git \
    libgomp1 \
    tesseract-ocr \
    && rm -rf /var/lib/apt/lists/*

# Create non-root user for Choreo
RUN useradd -r -u 10014 -g users choreouser

# Copy entire backend directory
COPY . .

# Install Python dependencies
RUN pip install --no-cache-dir -r choreo-ai-assistant/requirements.txt && \
    pip install --no-cache-dir -r diagram_processor/requirements.txt

# Set environment variables
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1

# Create necessary directories and set permissions
RUN mkdir -p /app/diagram_processor/output/summaries \
    /app/diagram_processor/output/graphs \
    /app/diagram_processor/output/extracted_text \
    /app/credentials \
    /app/logs \
    /tmp \
    && chown -R 10014:users /app /tmp

# Make start script executable
RUN chmod +x /app/start.py

# Switch to non-root user
USER 10014

# Health check for Choreo - dynamically uses PORT env var
HEALTHCHECK --interval=30s --timeout=30s --start-period=90s --retries=5 \
    CMD curl -f http://localhost:${PORT:-9090}/ || exit 1

# Expose port (will be overridden by Choreo's PORT env var)
EXPOSE 9090

# Start the backend server using startup script that reads PORT env var
CMD ["python3", "start.py"]

