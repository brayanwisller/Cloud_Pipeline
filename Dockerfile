FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Garante que a pasta de dados existe e tem permissão
RUN mkdir -p /app/data && chmod 777 /app/data

ENV DATA_DIR=/app/data

EXPOSE 8000

CMD ["gunicorn", "--bind", "0.0.0.0:8000", "app.wsgi:app"]