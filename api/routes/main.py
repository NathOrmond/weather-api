import os
from api.docs.templates import REDOC_HTML
from flask import Blueprint, Response, current_app
import logging

logger = logging.getLogger(__name__)

# Define the Blueprint for main application routes (like home, docs)
# 'main' is the name of the blueprint, used internally by Flask.
# __name__ helps Flask locate templates/static files if needed relative to this blueprint.
main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def home():
    """Serves the basic health/info endpoint."""
    logger.debug("Request received for blueprint / route")
    flask_env = os.environ.get('FLASK_ENV', 'development')
    endpoints = []
    
    # Get the Flask app from current_app instead of importing app directly
    for rule in current_app.url_map.iter_rules():
        endpoint = str(rule.endpoint)
        path = str(rule.rule)
        if (endpoint != 'static' and 
            not endpoint.startswith('_') and 
            not path.startswith('/static') and
            not '__debugger__' in path):
            endpoints.append({
                'endpoint': endpoint,
                'path': path,
                'methods': list(rule.methods - {'HEAD', 'OPTIONS'}) if rule.methods else []
            })
    
    # Check if specification is available in the current app's context
    if hasattr(current_app, 'specification'):
        api_paths = current_app.specification.get('paths', {})
        for path, methods in api_paths.items():
            for method, details in methods.items():
                if method.upper() in {'GET', 'POST', 'PUT', 'DELETE', 'PATCH'}:
                    endpoints.append({
                        'endpoint': details.get('operationId', f"{method} {path}"),
                        'path': path,
                        'methods': [method.upper()],
                        'description': details.get('summary', '')
                    })
    endpoints.sort(key=lambda x: x['path'])
    return {
        'health': 'OK',
        'environment': flask_env,
        'docs': {
            'redoc': '/docs',
            'swagger': '/ui'
        },
        'endpoints': endpoints
    }


@main_bp.route('/docs')
def redoc_ui():
    """Serves the Redoc API documentation UI."""
    logger.debug("Request received for blueprint /docs route")
    return Response(REDOC_HTML, mimetype='text/html')

