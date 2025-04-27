"""
WSGI entry point for production deployment
This file imports the Flask application from app.py and makes it available
for WSGI servers like Gunicorn, uWSGI, or mod_wsgi.
"""

# Import the Flask application from app.py
# All routes and configurations from app.py are automatically included
from app import app as application
import os

# Get environment variables with defaults
FLASK_ENV = os.environ.get('FLASK_ENV', 'production')
print(f"WSGI application loaded in {FLASK_ENV} mode")

# The 'application' object is what WSGI servers look for by convention

if __name__ == "__main__":
    # This block allows you to run the application directly with 'python wsgi.py'
    # It's mainly for testing - in production, you'd use gunicorn or uwsgi
    port = int(os.environ.get('PORT', 5000))
    host = os.environ.get('HOST', '0.0.0.0')
    application.run(host=host, port=port)
