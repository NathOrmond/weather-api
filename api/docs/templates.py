"""
HTML templates for API documentation.
"""

# ReDoc HTML template for the /docs endpoint
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