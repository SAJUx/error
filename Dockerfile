# Python base image ব্যবহার করুন
FROM python:3.9-slim

# Working directory Set করুন
WORKDIR /app

# System packages install করুন
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Python dependencies copy করুন
COPY requirements.txt .

# Python packages install করুন
RUN pip install --no-cache-dir -r requirements.txt

# Application code copy করুন
COPY . .

# Environment variables set করুন
ENV PORT=5000
ENV PYTHONUNBUFFERED=1

# Port expose করুন
EXPOSE 5000

# Application start করুন
CMD ["python", "app.py"]
