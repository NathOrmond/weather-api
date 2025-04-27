# File: api/routes/__init__.py

from flask import Flask

def register_routes(app: Flask):
    """
    Registers all the custom Flask Blueprints defined in the routes module
    with the main Flask application instance.

    Args:
        app: The Flask application instance obtained from Connexion.
    """
    from .main import main_bp  

    # Register the imported blueprint(s) with the Flask app
    # You can add url_prefix if desired, e.g., app.register_blueprint(main_bp, url_prefix='/custom')
    app.register_blueprint(main_bp)
