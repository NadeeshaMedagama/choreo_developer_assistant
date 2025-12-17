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

# Switch to non-root user
USER 10014

# Health check for Choreo
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:9090/health || exit 1

# Expose port
EXPOSE 9090

# Start the backend server
CMD ["uvicorn", "backend.app:app", "--host", "0.0.0.0", "--port", "9090"]
