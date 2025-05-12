# 1. Base image with Python
FROM python:3.11-slim

# 2. Set working dir
WORKDIR /app

# 3. Install system deps (Postgres client for healthchecks or migrations, if needed)
RUN apt-get update \
 && apt-get install -y --no-install-recommends gcc libpq-dev \
 && rm -rf /var/lib/apt/lists/*

# 4. Copy requirements and install
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 5. Copy application code
COPY . .

# 6. Expose the port
EXPOSE 8000

# 7. Use Uvicorn to run the app
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
