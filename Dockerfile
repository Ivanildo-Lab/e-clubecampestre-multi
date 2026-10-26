# =====================================================================
# Dockerfile para Django + MySQL + WeasyPrint (e-clubecampestre-multi)
# Projeto: clube_manager  |  Django 5.2  |  Python 3.12
# Settings: clube_manager.settings  |  WSGI: clube_manager.wsgi:application
# =====================================================================

# ---------------------- Estágio de BUILD (compila mysqlclient + deps weasyprint) -----
FROM python:3.12-slim AS builder

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /build

# Dependências de compilação do mysqlclient + weasyprint (pango, cairo, gdk-pixbuf, libffi)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    default-libmysqlclient-dev \
    pkg-config \
    libpango-1.0-0 \
    libcairo2 \
    libgdk-pixbuf-2.0-0 \
    libffi-dev \
    shared-mime-info \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --prefix=/install -r requirements.txt

# ---------------------- Estágio FINAL (leve) ------------------------
FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# Runtime: mysqlclient + weasyprint runtime libs
RUN apt-get update && apt-get install -y --no-install-recommends \
    libmariadb3 \
    libpango-1.0-0 \
    libpangoft2-1.0-0 \
    libcairo2 \
    libgdk-pixbuf-2.0-0 \
    libffi8 \
    libharfbuzz0b \
    libfontconfig1 \
    libfreetype6 \
    shared-mime-info \
    && rm -rf /var/lib/apt/lists/*

COPY --from=builder /install /usr/local

COPY . .

# Garante pastas de staticfiles e media
RUN mkdir -p staticfiles media logs

EXPOSE 8000

# Entrypoint: migrações + collectstatic + gunicorn
CMD ["sh", "-c", "\
    python manage.py migrate --noinput && \
    python manage.py collectstatic --noinput && \
    gunicorn clube_manager.wsgi:application \
      --bind 0.0.0.0:8000 \
      --workers ${GUNICORN_WORKERS:-2} \
      --timeout ${GUNICORN_TIMEOUT:-120} \
      --access-logfile - \
      --error-logfile -"]