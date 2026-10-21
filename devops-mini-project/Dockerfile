FROM python:3.14-slim
ARG APP_VERSION=local
ARG BUILD_TIME=unknown
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    APP_VERSION=${APP_VERSION} \
    BUILD_TIME=${BUILD_TIME} \
    PORT=10000
LABEL org.opencontainers.image.title="DevOps Mini Project" \
      org.opencontainers.image.revision=${APP_VERSION} \
      org.opencontainers.image.created=${BUILD_TIME}
WORKDIR /app
COPY requirements.txt .
RUN python -m pip install --no-cache-dir -r requirements.txt \
    && useradd --create-home --uid 10001 appuser
COPY app.py gunicorn.conf.py ./
COPY templates/ templates/
COPY static/ static/
COPY scripts/container_health.py scripts/container_health.py
USER appuser
EXPOSE 10000
HEALTHCHECK --interval=30s --timeout=5s --start-period=15s --retries=3 \
  CMD ["python", "scripts/container_health.py"]
CMD ["gunicorn", "--config", "gunicorn.conf.py", "app:app"]
