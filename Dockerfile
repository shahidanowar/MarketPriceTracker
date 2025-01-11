# Use Python 3.9 slim image
FROM python:3.9-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender1 \
    libgl1-mesa-glx \
    libgomp1 \
    git \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application
COPY . .

# Create necessary directories
RUN mkdir -p static uploads templates

# Set environment variables
ENV PORT=5000
ENV FLASK_APP=app.py
ENV FLASK_ENV=production

# Expose the port
EXPOSE 5000

# Command to run the application
CMD gunicorn app:app --bind 0.0.0.0:$PORT --workers 2 --threads 2 --timeout 120
