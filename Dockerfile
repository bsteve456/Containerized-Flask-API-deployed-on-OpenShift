# 1. Base Image - Start with Python
FROM python:3.9-slim

# 2. Set Working Directory inside container
WORKDIR /app

# 3. Copy requirements first
COPY requirements.txt .

# 4. Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# 5. Copy entire project
COPY . .

# 6. Tell container to listen on port 5000
EXPOSE 5000

# 7. Environment variables
ENV FLASK_APP=app/main.py
ENV PYTHONUNBUFFERED=1

# 8. When container starts, run Flask app
CMD ["python", "app/main.py"]