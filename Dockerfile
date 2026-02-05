# Python base image
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Don't write .pyc files
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy source code
COPY src/ ./src/

# Create data directory
RUN mkdir -p data

# Run the bot
CMD ["python", "-m", "src.main"]
