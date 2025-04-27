import connexion
from connexion.resolver import RestyResolver
import os
import yaml
from flask import jsonify
from api.routes import register_all_routes

# Read environment variables with defaults
FLASK_ENV = os.environ.get('FLASK_ENV', 'development')
DEBUG = os.environ.get('DEBUG', 'false').lower() == 'true'
LOG_LEVEL = os.environ.get('LOG_LEVEL', 'info')
PORT = int(os.environ.get('PORT', 5000))
HOST = os.environ.get('HOST', '0.0.0.0')
ENABLE_SWAGGER = os.environ.get('ENABLE_SWAGGER', 'true').lower() == 'true'
CORS_ALLOW_ALL = os.environ.get('CORS_ALLOW_ALL', 'true').lower() == 'true'

# Print environment for debugging
print(f"Starting application in {FLASK_ENV} mode")
print(f"Debug mode: {DEBUG}")
print(f"Log level: {LOG_LEVEL}")
print(f"Swagger UI enabled: {ENABLE_SWAGGER}")

def create_app():
    """Create and configure the Connexion app."""
    specification_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'docs/openapi')
    print(f"Using OpenAPI specification directory: {specification_dir}")
    
    app = connexion.App(__name__,
                      specification_dir=specification_dir)

    # Configure CORS if enabled
    if CORS_ALLOW_ALL:
        from flask_cors import CORS
        CORS(app.app)
    elif os.environ.get('ALLOWED_ORIGINS'):
        from flask_cors import CORS
        allowed_origins = os.environ.get('ALLOWED_ORIGINS').split(',')
        CORS(app.app, resources={r"/*": {"origins": allowed_origins}})
        print(f"CORS enabled for origins: {allowed_origins}")

    # Add the API with explicit options - no base_path to keep it simple
    app.add_api('specification.yaml',
              resolver=RestyResolver('api.controllers'),
              validate_responses=True,
              strict_validation=True,
              options={
                  "swagger_ui": ENABLE_SWAGGER,
                  "swagger_url": "/ui",
                  "openapi_json_url": "/openapi.json",  # Specify the exact URL for the spec
                  "redoc_options": {
                      "generate_code_examples": {
                          "languages": ["curl", "python", "javascript"],
                          "useBodyAndHeaders": True
                      }
                  }
              })
    
    # Register all application routes
    register_all_routes(app)
    return app

# Create the application instance
app = create_app()

if __name__ == '__main__':
    print("Registered routes (Note: May not show all Connexion routes):")
    for rule in app.app.url_map.iter_rules():
        if rule.endpoint != 'static':
             print(f"{rule.endpoint}: {rule.rule}")

    # For development with auto-reload, use a simple solution that works in Docker
    if DEBUG:
        # Use Flask's built-in server for development with reload
        # This avoids the Uvicorn reload problem in Docker
        app.app.run(host=HOST, port=PORT, debug=True)
    else:
        # Use Connexion's server for production (which uses Uvicorn)
        app.run(host=HOST, port=PORT, log_level=LOG_LEVEL.lower())

