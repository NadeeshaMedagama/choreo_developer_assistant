# Choreo-Optimized Dockerfile
# Deploy entire project structure, run only backend server

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

# Copy entire project structure (needed for imports)
COPY . .

# Install Python dependencies from both requirements files
RUN pip install --no-cache-dir -r requirements.txt || \
    pip install --no-cache-dir -r choreo-ai-assistant/requirements.txt

# Install diagram processor dependencies
RUN pip install --no-cache-dir -r diagram_processor/requirements.txt

# Set environment variables
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1
ENV PORT=9090

# Create necessary directories
RUN mkdir -p /app/diagram_processor/output/summaries \
    /app/diagram_processor/output/graphs \
    /app/diagram_processor/output/extracted_text \
    /app/credentials \
    /tmp

# Health check for Choreo
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:9090/health || exit 1

# Expose Choreo's default port
EXPOSE 9090

# Start the backend server
CMD ["uvicorn", "backend.app:app", "--host", "0.0.0.0", "--port", "9090"]
