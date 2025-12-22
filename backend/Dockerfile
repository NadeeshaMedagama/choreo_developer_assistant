FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies and clean up immediately
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    gcc \
    g++ \
    git \
    libgomp1 \
    tesseract-ocr \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean \
    && rm -rf /var/cache/apt/*

# Create non-root user for Choreo
RUN useradd -r -u 10014 -g users choreouser

# Copy entire backend directory
COPY . .

# AGGRESSIVE DISK SPACE OPTIMIZATION
# Install PyTorch CPU-only first (saves ~2GB)
RUN pip install --no-cache-dir torch==2.5.1 --index-url https://download.pytorch.org/whl/cpu && \
    pip cache purge && \
    rm -rf /root/.cache/pip/* /tmp/pip-* && \
    find / -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true

# Install backend dependencies in chunks to avoid disk space issues
RUN grep -v "^torch\|^sentence-transformers" choreo-ai-assistant/requirements.txt > /tmp/core-requirements.txt && \
    pip install --no-cache-dir -r /tmp/core-requirements.txt && \
    pip cache purge && \
    rm -rf /root/.cache/pip/* /tmp/pip-* /tmp/core-requirements.txt && \
    find / -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true

# Install sentence-transformers separately with cleanup
RUN pip install --no-cache-dir sentence-transformers>=2.2.2 && \
    pip cache purge && \
    rm -rf /root/.cache/pip/* /tmp/pip-* && \
    find / -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true

# Install diagram processor requirements
RUN pip install --no-cache-dir -r diagram_processor/requirements.txt && \
    pip cache purge && \
    rm -rf /root/.cache/pip/* /tmp/pip-* && \
    find / -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true

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

