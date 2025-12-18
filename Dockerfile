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

# Create non-root user
RUN useradd -r -u 10014 -g users appuser

# Copy entire project structure
COPY . .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt || \
    pip install --no-cache-dir -r backend/choreo-ai-assistant/requirements.txt

RUN pip install --no-cache-dir -r backend/diagram_processor/requirements.txt

# Set environment variables
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1
ENV PORT=9090

# Create necessary directories and set permissions
RUN mkdir -p /app/backend/diagram_processor/output/summaries \
    /app/backend/diagram_processor/output/graphs \
    /app/backend/diagram_processor/output/extracted_text \
    /app/credentials \
    /tmp \
    && chown -R 10014:users /app /tmp

# Make start scripts executable
RUN chmod +x /app/start.sh /app/start.py

# Switch to non-root user
USER 10014

# Health check for Choreo - use PORT environment variable with fallback
HEALTHCHECK --interval=30s --timeout=30s --start-period=90s --retries=5 \
    CMD curl -f http://localhost:${PORT:-9090}/ || exit 1

# Expose port (Choreo will override with actual port)
EXPOSE ${PORT:-9090}

# Start the backend server using Python startup script that reads PORT env var
CMD ["python3", "/app/start.py"]
