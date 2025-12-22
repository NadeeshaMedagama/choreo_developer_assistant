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
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Create non-root user
RUN useradd -r -u 10014 -g users appuser

# Copy requirements files first (for better layer caching)
COPY backend/requirements.txt /tmp/backend-requirements.txt
COPY backend/diagram_processor/requirements.txt /tmp/diagram-requirements.txt

# Install PyTorch CPU-only version first (much smaller than CUDA version - ~200MB vs 2GB+)
RUN pip install --no-cache-dir torch==2.5.1 --index-url https://download.pytorch.org/whl/cpu && \
    pip cache purge

# Install backend dependencies (excluding torch since we installed CPU version above)
RUN grep -v "^torch" /tmp/backend-requirements.txt > /tmp/backend-requirements-no-torch.txt && \
    pip install --no-cache-dir -r /tmp/backend-requirements-no-torch.txt && \
    pip cache purge

# Install diagram processor dependencies
RUN pip install --no-cache-dir -r /tmp/diagram-requirements.txt && \
    pip cache purge && \
    rm -rf /tmp/*.txt /root/.cache

# Copy entire project structure
COPY . .


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

# Make start script executable
RUN chmod +x /app/start.py

# Switch to non-root user
USER 10014

# Health check for Choreo - use PORT environment variable with fallback
HEALTHCHECK --interval=30s --timeout=30s --start-period=90s --retries=5 \
    CMD curl -f http://localhost:${PORT:-9090}/ || exit 1

# Expose port (Choreo will override with actual port)
EXPOSE ${PORT:-9090}

# Start the backend server using Python startup script that reads PORT env var
CMD ["python3", "/app/start.py"]
