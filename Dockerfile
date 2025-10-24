FROM python:3.11-slim

WORKDIR /app

# Ensure predictable Python behavior
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt \
    && apt-get update \
    && apt-get install -y --no-install-recommends curl \
    && rm -rf /var/lib/apt/lists/*

COPY . .

# Configure Flask app discovery for CLI
ENV FLASK_APP=app.py

# Expose Flask default port
EXPOSE 5000

# Run the Flask dev server
CMD ["flask", "run", "--host=0.0.0.0", "--port=5000"]