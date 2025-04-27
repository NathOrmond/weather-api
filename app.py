# File: app.py

import connexion
from flask import Flask # Keep Flask import for type hinting if needed
from flask_cors import CORS
import os
from dotenv import load_dotenv
import logging
import uvicorn
from api.routes import register_routes
from api.repositories.seed import seed_data # Import seed function

env = os.environ.get('FLASK_ENV', 'development')
dotenv_path = f'.env.{env}'
if os.path.exists(dotenv_path):
    print(f"Loading environment variables from {dotenv_path}")
    load_dotenv(dotenv_path=dotenv_path, override=True)
else:
    print(f"Warning: {dotenv_path} not found. Using default environment variables.")

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

log_level = getattr(logging, LOG_LEVEL_STR, logging.INFO)
uvicorn_log_level = LOG_LEVEL_STR.lower() # Uvicorn expects lowercase log level names
logging.basicConfig(level=log_level, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logging.getLogger("uvicorn.error").setLevel(log_level)
logging.getLogger("uvicorn.access").setLevel(log_level)
logger = logging.getLogger(__name__) 

connexion_app = connexion.App(
    __name__,
    specification_dir='./docs/openapi/'
)

flask_app = connexion_app.app
# TODO: Add Flask configurations if necessary
# flask_app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'default-secret-key')


if CORS_ALLOW_ALL:
    CORS(flask_app)
    logger.info("CORS enabled for all origins.")
else:
    logger.info("CORS not enabled globally.")

connexion_api_options = {"swagger_ui": False}
connexion_app.add_api(
    'specification.yaml',
    resolver=connexion.RestyResolver('api.controllers'), 
    validate_responses=True,
    strict_validation=True,
    options=connexion_api_options
)
logger.info("Connexion API specification 'specification.yaml' added.")

register_routes(flask_app)
logger.info("Custom Flask routes registered.")

# --- Seed Initial Data ---
# Only seed in development environment
if env == 'development':
    seed_data()
    logger.info("Development data seeded successfully.")
else:
    logger.info("Skipping data seeding in non-development environment.")


if __name__ == '__main__':
    logger.info("Starting development server directly using Uvicorn...")
    print("\nRegistered routes (Flask URL Map):")
    for rule in flask_app.url_map.iter_rules():
         print(f"{rule.endpoint}: {rule.rule}")
    print("-" * 30)
    uvicorn.run(
        "app:app", 
        host=HOST,
        port=PORT,
        reload=DEBUG_MODE, 
        log_level=uvicorn_log_level
    )

# --- WSGI Entry Point ---
# Expose the Connexion app instance as 'app' for WSGI servers like Gunicorn
# This is the 'app' variable referenced in the uvicorn import string "app:app"
app = connexion_app

