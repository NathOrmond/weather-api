# File: app.py

import connexion
from flask import Flask, Response, render_template, current_app # Keep Flask import for type hinting if needed
from flask_cors import CORS
import os
from dotenv import load_dotenv
import logging
import uvicorn # <<< Import uvicorn

# --- Configuration Loading ---
# Determine environment and load .env file
env = os.environ.get('FLASK_ENV', 'development')
dotenv_path = f'.env.{env}'
if os.path.exists(dotenv_path):
    print(f"Loading environment variables from {dotenv_path}")
    load_dotenv(dotenv_path=dotenv_path, override=True)
else:
    print(f"Warning: {dotenv_path} not found. Using default environment variables.")

# Get config settings from environment with defaults
DEBUG_MODE = os.environ.get('DEBUG', 'false').lower() == 'true' # Used for reload flag
LOG_LEVEL_STR = os.environ.get('LOG_LEVEL', 'info').upper()
ENABLE_SWAGGER = os.environ.get('ENABLE_SWAGGER', 'false').lower() == 'true' # Note: We are using Redoc
CORS_ALLOW_ALL = os.environ.get('CORS_ALLOW_ALL', 'false').lower() == 'true'
HOST = os.environ.get('HOST', '0.0.0.0')
PORT = int(os.environ.get('PORT', 5000))

print(f"Starting application in {env} mode")
print(f"Debug mode (controls reload): {DEBUG_MODE}")
print(f"Log level: {LOG_LEVEL_STR}")
print(f"Swagger UI enabled (ignored for Redoc): {ENABLE_SWAGGER}")

# --- Logging Setup ---
log_level = getattr(logging, LOG_LEVEL_STR, logging.INFO)
uvicorn_log_level = LOG_LEVEL_STR.lower() # Uvicorn expects lowercase log level names
# Configure root logger
logging.basicConfig(level=log_level, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
# Configure uvicorn loggers to use the same level
logging.getLogger("uvicorn.error").setLevel(log_level)
logging.getLogger("uvicorn.access").setLevel(log_level)
logger = logging.getLogger(__name__) # Get logger for this module

# --- Initialize Connexion (Creates the Flask app internally) ---
connexion_app = connexion.App(
    __name__,
    specification_dir='./docs/openapi/'
)

# --- Access the underlying Flask app created by Connexion ---
flask_app = connexion_app.app
# Apply Flask configurations if necessary
# flask_app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'default-secret-key')


# --- Apply CORS to the Flask app ---
if CORS_ALLOW_ALL:
    CORS(flask_app)
    logger.info("CORS enabled for all origins.")
else:
    logger.info("CORS not enabled globally.")


# --- Add API spec to Connexion (Adds Connexion routes to flask_app) ---
connexion_api_options = {"swagger_ui": False}
connexion_app.add_api(
    'specification.yaml',
    resolver=connexion.RestyResolver('api.controllers'),
    validate_responses=True,
    strict_validation=True,
    options=connexion_api_options
)
logger.info("Connexion API specification 'specification.yaml' added.")


# --- Define Custom Flask Routes AFTER Connexion ---
@flask_app.route('/')
def home():
    """Serves the basic health/info endpoint."""
    logger.debug("Request received for / route")
    return {
        'health': 'OK',
        'message': 'API docs available at /docs'
    }

# Define the HTML template for Redoc
REDOC_HTML = """
<!DOCTYPE html>
<html>
  <head>
    <title>Weather API Docs</title>
    <meta charset="utf-8"/>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <link href="https://fonts.googleapis.com/css?family=Montserrat:300,400,700|Roboto:300,400,700" rel="stylesheet">
    <style> body { margin: 0; padding: 0; } </style>
  </head>
  <body>
    <redoc spec-url='/openapi.json'></redoc> <script src="https://cdn.redoc.ly/redoc/latest/bundles/redoc.standalone.js"> </script>
  </body>
</html>
"""

@flask_app.route('/docs')
def redoc_ui():
    """Serves the Redoc API documentation UI."""
    logger.debug("Request received for /docs route")
    return Response(REDOC_HTML, mimetype='text/html')


# --- Main execution block ---
# Use this block ONLY for running the app directly with 'python app.py'
if __name__ == '__main__':
    logger.info("Starting development server directly using Uvicorn...")

    print("\nRegistered routes (Flask URL Map):")
    for rule in flask_app.url_map.iter_rules():
         print(f"{rule.endpoint}: {rule.rule}")
    print("-" * 30)

    # Directly call uvicorn.run()
    # Pass the application as an import string 'app:app'
    # 'app:app' means: look in file 'app.py' for variable 'app'
    uvicorn.run(
        "app:app", # <<< Use import string
        host=HOST,
        port=PORT,
        reload=DEBUG_MODE, # Uvicorn uses 'reload'
        log_level=uvicorn_log_level
    )

# --- WSGI Entry Point ---
# Expose the Connexion app instance as 'app' for WSGI servers like Gunicorn
# This is the 'app' variable referenced in the uvicorn import string "app:app"
app = connexion_app

