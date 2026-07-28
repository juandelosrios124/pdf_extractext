# ──────────────────────────────────────────
# Etapa 1: builder — instala dependencias
# ──────────────────────────────────────────
FROM python:3.11-slim AS builder

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

COPY pyproject.toml uv.lock ./

RUN uv sync --frozen --no-install-project --no-dev


# ──────────────────────────────────────────
# Etapa 2: production — imagen final segura
# ──────────────────────────────────────────
FROM python:3.11-slim AS production

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Crear usuario sin privilegios CON home
RUN groupadd --gid 1001 appgroup && \
    useradd --uid 1001 --gid appgroup --create-home appuser

COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

COPY --from=builder /app/.venv /app/.venv

COPY app/ ./app/
COPY migrations/ ./migrations/
COPY pyproject.toml uv.lock ./

RUN uv sync --frozen --no-dev

RUN chown -R appuser:appgroup /app

USER appuser

EXPOSE 8000

# ✅ Verificar que la app responde correctamente
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/api/v1/health/')" \
    || exit 1

CMD ["uv", "run", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]

