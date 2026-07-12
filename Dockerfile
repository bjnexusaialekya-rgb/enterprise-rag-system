FROM python:3.12-slim

# Tesseract is required for OCR ingestion (pytesseract) — the old code had a
# hardcoded Windows path for this; install it as a system package instead.
RUN apt-get update && apt-get install -y --no-install-recommends \
    tesseract-ocr \
    libpq-dev \
    gcc \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

# Runs schema.sql on container start is NOT handled here — apply it once
# against your AWS RDS instance separately (see README / deployment notes).
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
