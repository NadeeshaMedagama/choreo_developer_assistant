FROM python:3.11-slim as builder

WORKDIR /app

# Install build-essential only for the build phase
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc g++ git curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements.txt first for better caching
COPY requirements.txt .

# Install dependencies with minimal cache and in one layer
RUN pip install --no-cache-dir -r requirements.txt && \
    pip cache purge || true

# --- Final Production Image ---
FROM python:3.11-slim

WORKDIR /app

# Install only runtime dependencies (tesseract-ocr and libgomp1)
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl libgomp1 tesseract-ocr \
    && rm -rf /var/lib/apt/lists/*

# Copy the installed python packages from the builder
COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# Set up user and permissions
RUN useradd -r -u 10014 -g users choreouser
COPY . .
RUN chown -R 10014:users /app

USER 10014
ENV PYTHONPATH=/app
ENV PORT=9090

CMD ["python", "-m", "uvicorn", "app:app", "--host", "0.0.0.0", "--port", "9090"]
