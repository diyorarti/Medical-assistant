# syntax=docker/dockerfile:1.6

# ---- Base Image ---- 
FROM python:3.11-slim AS runtime

# preventing Python from wrting .pyc files/enables unbuffered logs
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# system deps (curl for HEALTHCHECK)
RUN apt-get update && apt-get install -y --no-install-recommends curl \
    && rm -rf /var/lib/apt/lists/*

# creating and using a non-root user
RUN useradd -m -u 10001 appuser
WORKDIR /app 

# ----dependencies
COPY pyproject.toml poetry.lock* /app/
RUN pip install --upgrade pip && pip install .

# ----APP code ----
COPY ./api /app/api

# making sure the non-root owns the app dir
RUN chown -R appuser:appuser /app
USER appuser

# default port for uvicorn 
EXPOSE 8000

# basic healthchecking 
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
  CMD curl -fsS http://127.0.0.1:8000/health || exit 1

# api running 
CMD ["sh", "-c", "uvicorn api.main:app --host 0.0.0.0 --port ${PORT:-8000} --workers 2 --timeout-keep-alive 75"]
