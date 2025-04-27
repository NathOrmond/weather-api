# Official Python runtime 
FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE 1  # Prevents python from writing .pyc files
ENV PYTHONUNBUFFERED 1      # Prevents python from buffering stdout/stderr

WORKDIR /app

# Install system dependencies (Graphviz)
RUN apt-get update && \
    apt-get install -y --no-install-recommends graphviz && \
    rm -rf /var/lib/apt/lists/*

# Install Python dependencies
# Copy only requirements first to leverage Docker cache
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

COPY . .

# Create directory for diagrams
RUN mkdir -p /app/docs/architecture

# Run pyreverse to generate dot files targeting the 'api' package
# Output .dot files to the architecture directory
RUN pyreverse -o dot -p WeatherAPI api -d /app/docs/architecture

# Run dot to convert .dot files to PNG images
# Output .png files to the architecture directory
RUN dot -Tpng /app/docs/architecture/classes_WeatherAPI.dot -o /app/docs/architecture/classes.png && \
    dot -Tpng /app/docs/architecture/packages_WeatherAPI.dot -o /app/docs/architecture/packages.png

# Optional: Clean up .dot files if not needed in the final image
RUN rm /app/docs/architecture/*.dot

# For both Flask dev and Gunicorn
EXPOSE 5000

# Default command (can be overridden by docker-compose)
# IMPORTANTFor production, Gunicorn is recommended. Ensure wsgi.py exists and imports the app correctly.
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "wsgi:application"] 