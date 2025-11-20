# Use official lightweight Python image
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Copy requirements and install
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Set environment variables (defaults, can be overridden)
ENV PYTHONUNBUFFERED=1

# Command to run the application
# Note: For Cloud Run jobs, we run the script. 
# If we were deploying a server, we'd run gunicorn/uvicorn.
CMD ["python", "main.py"]
