# Flask API with Modular OpenAPI

This project demonstrates a Flask API with a modular OpenAPI specification structure.

## Project Structure

```
project/
├── api/
│   ├── controllers/      # API endpoint handlers
│   ├── models/           # Data models
│   ├── services/         # Business logic
│   ├── repositories/     # Data access
│   └── schemas/          # Serialization/deserialization
├── config/               # Configuration
├── docs/
│   └── openapi/          # OpenAPI specification files
├── scripts/              # Utility scripts
├── tests/                # Tests
├── app.py                # Application entry point
├── wsgi.py               # WSGI entry point
└── requirements.txt      # Dependencies
```

## Setup

1. Create a virtual environment:
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

3. Run the application:
   ```
   python app.py
   ```

4. Access the API documentation:
   Open your browser and navigate to http://localhost:5000/ui/

## OpenAPI Specification

The API is defined using a modular OpenAPI 3.0 specification:

- `docs/openapi/specification.yaml`: Main entry point
- `docs/openapi/paths/`: API endpoint definitions
- `docs/openapi/components/`: Reusable components (schemas, parameters, responses)

## Development

1. Define your API using the OpenAPI specification
2. Implement controllers to handle requests
3. Create models, services, and repositories as needed
4. Write tests to validate your implementation
