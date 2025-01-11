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
    wget \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Install PaddlePaddle first
RUN pip install --no-cache-dir paddlepaddle==2.5.1

# Copy requirements and install other dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application
COPY . .

# Create necessary directories
RUN mkdir -p static uploads templates

# Download and cache PaddleOCR model files
RUN python -c "from paddleocr import PaddleOCR; ocr = PaddleOCR(use_angle_cls=True, lang='en')"

# Set environment variables
ENV PORT=5000
ENV FLASK_APP=app.py
ENV FLASK_ENV=production
ENV PYTHONUNBUFFERED=1

# Expose the port
EXPOSE 5000

# Command to run the application
CMD gunicorn app:app --bind 0.0.0.0:$PORT --workers 1 --threads 4 --timeout 120
