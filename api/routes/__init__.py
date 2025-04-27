"""
Routes module for the API.

This module contains all route definitions and handlers for the API endpoints.
"""
import os
from flask import Response, url_for
from api.docs.templates import REDOC_HTML


def register_all_routes(app):
    """
    Register all API routes with the application.
    Args:
        app: The Connexion application instance
    """
    
    @app.route('/')
    def home():
        """Home/health endpoint that also provides information about API docs."""
        flask_env = os.environ.get('FLASK_ENV', 'development')
        endpoints = []
        for rule in app.app.url_map.iter_rules():
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
        if hasattr(app, 'specification'):
            api_paths = app.specification.get('paths', {})
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
    
    @app.route('/docs')
    def redoc_ui():
        """Serve the ReDoc UI documentation."""
        return Response(REDOC_HTML, mimetype='text/html') 