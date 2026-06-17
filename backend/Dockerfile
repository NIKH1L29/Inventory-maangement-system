# Lightweight Python image - good enough for FastAPI demos
FROM python:3.11-slim

WORKDIR /app

# Install deps first (Docker layer cache trick)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app ./app

# Render/Railway inject PORT; default 8000 for local docker run
ENV PORT=8000
EXPOSE 8000

# Run as module so imports resolve correctly
CMD ["sh", "-c", "uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}"]
