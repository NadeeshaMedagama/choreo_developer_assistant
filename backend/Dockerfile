FROM python:3.11-slim as builder

WORKDIR /app

# Install build-essential only for the build phase
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc g++ git curl \
    && rm -rf /var/lib/apt/lists/*

# Install heavy dependencies in one go to keep layer size down
RUN pip install --no-cache-dir torch==2.2.0+cpu --index-url https://download.pytorch.org/whl/cpu && \
    pip install --no-cache-dir \
    numpy scipy scikit-learn sentence-transformers \
    fastapi uvicorn langchain openai pymilvus \
    opencv-python-headless pytesseract pdf2image

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

CMD ["python3", "start.py"]