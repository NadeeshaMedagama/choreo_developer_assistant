FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies and clean up in same layer
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

# Create non-root user
RUN useradd -r -u 10014 -g users appuser

# Copy lightweight requirements files (requirements-docker.txt uses CPU-only versions)
COPY backend/requirements-docker.txt /tmp/backend-requirements.txt
COPY backend/diagram_processor/requirements.txt /tmp/diagram-requirements.txt

# AGGRESSIVE DISK SPACE OPTIMIZATION:
# Install dependencies in chunks with immediate cleanup to avoid disk space issues
# This prevents pip from downloading everything at once

# Step 1: Install PyTorch CPU-only (saves ~2GB vs CUDA version)
RUN pip install --no-cache-dir torch==2.5.1 --index-url https://download.pytorch.org/whl/cpu && \
    pip cache purge && \
    rm -rf /root/.cache/pip/* /tmp/pip-* && \
    find / -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true

# Step 2: Install core dependencies (lightweight packages first)
RUN grep -v "^torch\|^scipy\|^scikit-learn\|^sentence-transformers" /tmp/backend-requirements.txt > /tmp/core-requirements.txt && \
    pip install --no-cache-dir -r /tmp/core-requirements.txt && \
    pip cache purge && \
    rm -rf /root/.cache/pip/* /tmp/pip-* && \
    find / -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true

# Step 3: Install scipy separately (large package ~35MB)
RUN if grep -q "scipy" /tmp/backend-requirements.txt; then \
        pip install --no-cache-dir scipy && \
        pip cache purge && \
        rm -rf /root/.cache/pip/* /tmp/pip-*; \
    fi && \
    find / -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true

# Step 4: Install scikit-learn separately (large package ~9MB)
RUN if grep -q "scikit-learn" /tmp/backend-requirements.txt; then \
        pip install --no-cache-dir scikit-learn && \
        pip cache purge && \
        rm -rf /root/.cache/pip/* /tmp/pip-*; \
    fi && \
    find / -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true

# Step 5: Install sentence-transformers last (if needed)
RUN if grep -q "sentence-transformers" /tmp/backend-requirements.txt; then \
        pip install --no-cache-dir sentence-transformers && \
        pip cache purge && \
        rm -rf /root/.cache/pip/* /tmp/pip-*; \
    fi && \
    find / -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true

# Step 6: Install diagram processor dependencies
RUN pip install --no-cache-dir -r /tmp/diagram-requirements.txt && \
    pip cache purge && \
    rm -rf /tmp/*.txt /root/.cache/pip/* /tmp/pip-* && \
    find / -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true

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
