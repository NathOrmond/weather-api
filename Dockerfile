# Official Python runtime 
FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE 1  # Prevents python from writing .pyc files
ENV PYTHONUNBUFFERED 1      # Prevents python from buffering stdout/stderr

WORKDIR /app

# Install Python dependencies
# Copy only requirements first to leverage Docker cache
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

COPY . .

# For both Flask dev and Gunicorn
EXPOSE 5000

# Default command (can be overridden by docker-compose)
# IMPORTANTFor production, Gunicorn is recommended. Ensure wsgi.py exists and imports the app correctly.
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "wsgi:application"] 