# Dockerfile
FROM python:3.11-slim

# Variáveis de ambiente
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

RUN apt-get update && apt-get install -y \
    libpq-dev gcc netcat-traditional && \
    rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --upgrade pip && pip install -r requirements.txt

COPY . .

COPY <<EOF /app/wait-for-postgres.sh
#!/bin/sh
echo "Waiting for postgres..."

while ! nc -z db 5432; do
  sleep 0.1
done

echo "PostgreSQL started"

echo "Running migrations..."
python manage.py makemigrations
python manage.py migrate

echo "Starting server..."
exec gunicorn djangoibge.wsgi:application --bind 0.0.0.0:8000
EOF

RUN chmod +x /app/wait-for-postgres.sh

CMD ["/app/wait-for-postgres.sh"]
