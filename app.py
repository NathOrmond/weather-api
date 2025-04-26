import connexion
from connexion.resolver import RestyResolver
from flask import Response  
import os

app = connexion.App(__name__,
                    specification_dir='./docs/openapi/')

app.add_api('specification.yaml',
            resolver=RestyResolver('api.controllers'),
            validate_responses=True,
            strict_validation=True,
            options={
                "swagger_ui": True,
                "swagger_url": "/docs",
                "redoc_options": {
                    "generate_code_examples": {
                        "languages": ["curl", "python", "javascript"],
                        "useBodyAndHeaders": True
                    }
                }
            })

@app.route('/')
def home():
    return {
        'health': 'OK',
        'message': 'API docs available at /docs or /ui (swagger)'
    }


# TODO: move to a separate file
REDOC_HTML = """
<!DOCTYPE html>
<html>
  <head>
    <title>Weather API Docs</title>
    <meta charset="utf-8"/>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <link href="https://fonts.googleapis.com/css?family=Montserrat:300,400,700|Roboto:300,400,700" rel="stylesheet">

    <style>
      body {
        margin: 0;
        padding: 0;
      }
    </style>
  </head>
  <body>
    <redoc
        spec-url='/openapi.json'
        path-in-middle-panel="true"
        hide-download-button="true"
        expand-responses="all"
        required-props-first="true"
        generate-code-samples='{ "languages": [ {"lang": "curl"}, {"lang": "python"}, {"lang": "javascript"} ], "theme": "dark" }'
    ></redoc>
    <script src="https://cdn.redoc.ly/redoc/latest/bundles/redoc.standalone.js"> </script>
  </body>
</html>
"""

@app.route('/docs')
def redoc_ui():
    return Response(REDOC_HTML, mimetype='text/html')

if __name__ == '__main__':
    print("Registered routes (Note: May not show all Connexion routes):")
    for rule in app.app.url_map.iter_rules():
        if rule.endpoint != 'static':
             print(f"{rule.endpoint}: {rule.rule}")

    app.run(port=5000, log_level="info")

