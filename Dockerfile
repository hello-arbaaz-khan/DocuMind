FROM python:3.12-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    libpq-dev \
    gcc \
    build-essential \
    git \
    && rm -rf /var/lib/apt/lists/*

# Install Django and Google Drive/Celery dependencies
COPY requirements.txt .
COPY drive_service/requirements.txt /tmp/drive-requirements.txt

RUN pip install --no-cache-dir torch \
    --index-url https://download.pytorch.org/whl/cpu

RUN pip install --no-cache-dir --timeout 300 --retries 5 \
    -r requirements.txt \
    -r /tmp/drive-requirements.txt

# Copy project
COPY . .

EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:8000', timeout=5)" || exit 1

CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]