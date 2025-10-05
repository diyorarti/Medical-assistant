# Dockerfile
FROM python:3.11-slim

# System deps (optional but useful for httpx + SSL)
RUN apt-get update && apt-get install -y --no-install-recommends \
    ca-certificates curl && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy and install deps first (better layer caching)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy app source
COPY src ./src

# App env
ENV PYTHONUNBUFFERED=1 \
    PORT=8080

# Expose port (for local clarity; platforms often ignore)
EXPOSE 8080

# Run the server
CMD ["uvicorn", "src.app:app", "--host", "0.0.0.0", "--port", "8080"]
