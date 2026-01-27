FROM python:3.11-slim

# Set Python to run unbuffered for proper Docker logging
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

# Install dependencies for OCR and image processing
RUN apt-get update && apt-get install -y \
    tesseract-ocr \
    tesseract-ocr-eng \
    libgl1 \
    libglib2.0-0 \
    curl \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy requirements files
COPY requirements.txt .
COPY requirements-core.txt .

# Upgrade pip first
RUN pip install --upgrade pip setuptools wheel

# Install core requirements first (smaller, faster)
RUN pip install --no-cache-dir \
    --default-timeout=100 \
    --retries=5 \
    -r requirements-core.txt

# Install remaining requirements (with fallback)
RUN pip install --no-cache-dir \
    --default-timeout=100 \
    --retries=5 \
    -r requirements.txt || \
    (echo "Retrying with individual packages..." && \
     pip install --no-cache-dir --default-timeout=100 opencv-python==4.8.1.78 && \
     pip install --no-cache-dir --default-timeout=100 pytesseract==0.3.10 && \
     pip install --no-cache-dir --default-timeout=100 Pillow==10.1.0 && \
     pip install --no-cache-dir --default-timeout=100 reportlab==4.0.7 && \
     pip install --no-cache-dir --default-timeout=100 imagehash==4.3.1 && \
     pip install --no-cache-dir --default-timeout=100 numpy==1.24.3 && \
     pip install --no-cache-dir --default-timeout=100 scikit-learn==1.3.2)

# Copy application code
COPY . .

# Create necessary directories
RUN mkdir -p uploads logs

EXPOSE 5000

CMD ["python", "-m", "flask", "run", "--host=0.0.0.0", "--port=5000"]