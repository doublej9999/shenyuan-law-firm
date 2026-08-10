FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    APP_ENV=production

WORKDIR /app

COPY requirements.lock .
RUN pip install --no-cache-dir -r requirements.lock

COPY app ./app
COPY index.html .
COPY admin.html .
COPY admin_marketing.html .
COPY admin_research.html .
COPY wechat-qrcode.png .
COPY content ./content
COPY legal_kb ./legal_kb
COPY docs/handbook ./docs/handbook

# Non-root user + writable data dir (WAL mode also needs write access there).
RUN mkdir -p /app/data \
    && useradd --create-home --uid 10001 appuser \
    && chown -R appuser:appuser /app
USER appuser

EXPOSE 8000

# Single worker on purpose: SQLite is a single-writer file, and the per-IP
# rate limit buckets live in-process.
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--proxy-headers"]
