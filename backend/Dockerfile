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

# Copy requirements files first for better caching
COPY choreo-ai-assistant/requirements.txt /tmp/backend-requirements.txt
COPY diagram_processor/requirements.txt /tmp/diagram-requirements.txt

# AGGRESSIVE DISK SPACE OPTIMIZATION
# Step 1: Install PyTorch CPU-only FIRST (saves ~2.8GB vs CUDA version)
RUN pip install --no-cache-dir \
    torch==2.2.0+cpu \
    --index-url https://download.pytorch.org/whl/cpu && \
    pip cache purge && \
    rm -rf /root/.cache/pip/* /tmp/pip-* /root/.cache/huggingface && \
    find /usr/local/lib/python3.11 -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true && \
    find /usr/local/lib/python3.11 -type d -name "tests" -exec rm -rf {} + 2>/dev/null || true

# Step 2: Install numpy and core scientific packages
RUN pip install --no-cache-dir \
    'numpy>=1.24.0,<2.0.0' \
    scipy \
    scikit-learn && \
    pip cache purge && \
    rm -rf /root/.cache/pip/* /tmp/pip-* && \
    find /usr/local/lib/python3.11 -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true

# Step 3: Install sentence-transformers (depends on torch, numpy)
RUN pip install --no-cache-dir \
    'sentence-transformers>=2.2.0' && \
    pip cache purge && \
    rm -rf /root/.cache/pip/* /tmp/pip-* /root/.cache/huggingface && \
    find /usr/local/lib/python3.11 -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true

# Step 4: Install fastapi and web framework dependencies
RUN pip install --no-cache-dir \
    'fastapi>=0.100.0,<1.0.0' \
    'uvicorn[standard]>=0.25.0' \
    'httpx>=0.25.0' \
    'aiohttp>=3.9.0' \
    'requests>=2.31.0' \
    'python-dotenv>=1.0.0' \
    'psutil>=5.9.0' && \
    pip cache purge && \
    rm -rf /root/.cache/pip/* /tmp/pip-* && \
    find /usr/local/lib/python3.11 -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true

# Step 5: Install LangChain ecosystem (larger packages) - let pip resolve versions
RUN pip install --no-cache-dir \
    'langchain>=0.1.0' \
    'langchain-core>=0.1.0' \
    'langchain-community>=0.0.20' \
    'langchain-openai>=0.0.5' \
    'langgraph>=0.0.20' \
    'openai>=1.0.0' && \
    pip cache purge && \
    rm -rf /root/.cache/pip/* /tmp/pip-* && \
    find /usr/local/lib/python3.11 -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true

# Step 6: Install remaining backend dependencies
RUN pip install --no-cache-dir \
    'pymilvus>=2.3.0' \
    'google-cloud-vision>=3.4.0' \
    'Pillow>=10.0.0' && \
    pip cache purge && \
    rm -rf /root/.cache/pip/* /tmp/pip-* && \
    find /usr/local/lib/python3.11 -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true

# Step 7: Install diagram processor dependencies (lightweight)
RUN pip install --no-cache-dir \
    'pytesseract>=0.3.10' \
    'pdf2image>=1.16.0' \
    'opencv-python-headless>=4.8.0' \
    'python-docx>=1.0.0' \
    'python-pptx>=0.6.21' \
    'openpyxl>=3.0.0' \
    'PyPDF2>=3.0.0' \
    'networkx>=3.0.0' \
    'pydot>=1.4.0' \
    'lxml>=4.9.0' \
    'beautifulsoup4>=4.12.0' \
    'tqdm>=4.65.0' \
    'pyyaml>=6.0.0' && \
    pip cache purge && \
    rm -rf /tmp/*.txt /root/.cache/pip/* /tmp/pip-* && \
    find /usr/local/lib/python3.11 -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true

# Final cleanup - remove build artifacts and unnecessary files
RUN find /usr/local/lib/python3.11 -type f -name '*.pyc' -delete && \
    find /usr/local/lib/python3.11 -type d -name "tests" -exec rm -rf {} + 2>/dev/null || true && \
    find /usr/local/lib/python3.11 -type d -name "test" -exec rm -rf {} + 2>/dev/null || true && \
    rm -rf /root/.cache/* /tmp/*

# Copy entire backend directory
COPY . .

# Set environment variables
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1
ENV PORT=9090

# Create necessary directories and set permissions
RUN mkdir -p /app/diagram_processor/output/summaries \
    /app/diagram_processor/output/graphs \
    /app/diagram_processor/output/extracted_text \
    /app/credentials \
    /app/logs \
    /tmp \
    && chown -R 10014:users /app /tmp

# Make start script executable if it exists
RUN if [ -f /app/start.py ]; then chmod +x /app/start.py; fi

# Switch to non-root user
USER 10014

# Health check for Choreo - dynamically uses PORT env var
HEALTHCHECK --interval=30s --timeout=30s --start-period=90s --retries=5 \
    CMD curl -f http://localhost:${PORT:-9090}/ || exit 1

# Expose port (will be overridden by Choreo's PORT env var)
EXPOSE 9090

# Start the backend server using start.py which reads PORT env var
CMD ["python3", "start.py"]

