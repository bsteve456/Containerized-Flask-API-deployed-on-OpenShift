FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 5000

ENV FLASK_APP=app/main.py
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app

CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "4", "app.main:app"]