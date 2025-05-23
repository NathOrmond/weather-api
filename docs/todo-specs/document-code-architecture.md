# Technical Specification: Integrating Pyreverse Architecture Diagrams

## 1. Introduction

This document outlines the process for integrating automated code architecture diagram generation into the Weather API project using Pyreverse (part of Pylint) and Graphviz. The generated UML diagrams (class and package diagrams) will provide visual insights into the codebase structure and will be accessible via a dedicated web endpoint within the application.

## 2. Objective

-   Automatically generate UML class and package diagrams from the application's Python source code (specifically the `api` package/module).
-   Make these diagrams accessible to developers via a web interface served by the Flask application at the `/docs/architecture` route.
-   Integrate the necessary tools and the diagram generation process into the existing Docker setup for consistency across environments.

## 3. Prerequisites

-   **Pylint:** Must be installed in the environment where diagrams are generated (local development environment and Docker image). Pyreverse is included with Pylint.
-   **Graphviz:** Must be installed on the system or within the Docker image to render the `.dot` files generated by Pyreverse into image formats (e.g., PNG, SVG).
-   **Project Structure:** Assumes the primary Python source code to be analyzed resides in a directory named `api` within the project root.

## 4. Implementation Steps

### 4.1. Install Dependencies

**a) Local Development:**
   Ensure `pylint` is included in your `requirements.txt` or install manually:
   ```bash
   pip install pylint
Install Graphviz based on your OS (see previous instructions).b) Dockerfile:Modify the Dockerfile to install pylint via pip and graphviz via the package manager (apt-get for the python:3.11-slim base image).# FILE: Dockerfile (Additions/Modifications)

# ... (FROM, ENV, WORKDIR) ...

# Install system dependencies (Graphviz)
RUN apt-get update && \
    apt-get install -y --no-install-recommends graphviz && \
    rm -rf /var/lib/apt/lists/*

# Install Python dependencies (including pylint)
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir pylint && \ # Ensure pylint is installed
    pip install --no-cache-dir -r requirements.txt

# ... (COPY ., EXPOSE) ...

# --- NEW: Generate Diagrams During Build ---
# Create directory for diagrams
RUN mkdir -p /app/static/architecture

# Run pyreverse to generate dot files targeting the 'api' package
# Output .dot files to the architecture directory
RUN pyreverse -o dot -p WeatherAPI api -d /app/static/architecture

# Run dot to convert .dot files to PNG images
# Output .png files to the architecture directory
RUN dot -Tpng /app/static/architecture/classes_WeatherAPI.dot -o /app/static/architecture/classes.png && \
    dot -Tpng /app/static/architecture/packages_WeatherAPI.dot -o /app/static/architecture/packages.png

# Optional: Clean up .dot files if not needed in the final image
RUN rm /app/static/architecture/*.dot
# --- END NEW ---

# Default command (Gunicorn for prod)
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "wsgi:application"]
4.2. Create HTML TemplateCreate an HTML file to display the diagrams.File: templates/architecture.html (Create the templates directory if it doesn't exist)<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>API Architecture Diagrams</title>
    <style>
        body { font-family: sans-serif; margin: 20px; }
        h1, h2 { border-bottom: 1px solid #ccc; padding-bottom: 5px; }
        .diagram { margin-bottom: 30px; text-align: center; }
        .diagram img { max-width: 100%; height: auto; border: 1px solid #eee; }
    </style>
</head>
<body>
    <h1>API Architecture Diagrams</h1>
    <p>These diagrams are automatically generated from the source code using Pyreverse and Graphviz.</p>

    <div class="diagram">
        <h2>Class Diagram</h2>
        <img src="{{ url_for('static', filename='architecture/classes.png') }}" alt="Class Diagram">
    </div>

    <div class="diagram">
        <h2>Package Diagram</h2>
        <img src="{{ url_for('static', filename='architecture/packages.png') }}" alt="Package Diagram">
    </div>

</body>
</html>
4.3. Update Flask Application (app.py)Modify app.py to add a route that renders the architecture.html template. Flask automatically serves files from a directory named static in the application root, which aligns with the Dockerfile changes. Ensure render_template is imported.# FILE: app.py (Additions)

# Add near the top with other imports
from flask import render_template

# ... (Existing Connexion app setup, other routes) ...

# --- NEW: Architecture Docs Route ---
@app.route('/docs/architecture')
def architecture_docs():
    """Serves the HTML page displaying architecture diagrams."""
    # Assumes diagrams are generated into static/architecture during build
    # Renders the template located in the 'templates' directory
    return render_template('architecture.html')
# --- END NEW ---


if __name__ == '__main__':
    # ... (Existing __main__ block) ...
    # Ensure host='0.0.0.0' is used if running directly
    app.run(host='0.0.0.0', port=5000, log_level="info")

Note: Ensure your connexion.App instance correctly integrates with the underlying Flask app (app.app) so that standard Flask routes like /docs/architecture work alongside Connexion-managed routes. The standard setup usually handles this correctly.5. VerificationBuild Docker Image: Run docker build -t weather-api-architecture . (or use docker-compose build). Check the build logs for successful execution of the RUN pyreverse and RUN dot commands without errors.Run Container: Start the container using docker run -p 5000:5000 weather-api-architecture or docker-compose up (using the appropriate profile).Access Endpoint: Navigate to http://localhost:5000/docs/architecture in your web browser.Check Content: Verify that the HTML page loads correctly and displays both the "Class Diagram" and "Package Diagram" images generated from your api package.6. Expected OutcomeThe Docker image build process will include the generation of classes.png and packages.png diagrams within the /app/static/architecture/ directory inside the image.The running application will serve an HTML page at /docs/architecture displaying these diagrams.Developers will have easy access to up-to-date visual representations of the code architecture.7. ConsiderationsDiagram Complexity: For very large codebases, the generated diagrams might become complex and hard to read. Pyreverse options (--filter-mode, --max-depth, etc.) can be used to simplify them if needed.Generation Time: Diagram generation adds time to the Docker build process.Target Package: Ensure the pyreverse command in the Dockerfile correctly targets the main source code package (e.g., api). Adjust if your code is structured differently.Output Format: PNG is used