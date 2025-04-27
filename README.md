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
│   ├── schemas/          # Serialization/deserialization
│   └── routes/           # Route definitions and handlers
├── config/               # Configuration
├── docs/
│   └── openapi/          # OpenAPI specification files
├── scripts/              
│   ├── combine_openapi.py  # Utility to combine OpenAPI files
│   ├── restart_docker-dev.sh # Script to restart development containers
│   └── debug-docker-dev.sh # Script to view development container logs
├── tests/                # Tests
├── app.py                # Application entry point (development)
├── wsgi.py               # WSGI entry point (production)
├── Dockerfile            # Docker configuration
├── docker-compose.yml    # Docker Compose configuration with profiles
├── .env.development      # Development environment variables
├── .env.production       # Production environment variables
└── requirements.txt      # Dependencies
```

## Running the Application

### 1. Local Development

The simplest way to run the application locally:

```bash
# Install dependencies
pip install -r requirements.txt

# Run the application
python app.py
```

The application will start on http://localhost:5000 by default.

### 2. Docker Development

For development with Docker:

```bash
# Use the convenience script to start the development container
./scripts/restart_docker-dev.sh

# Or manually with Docker Compose
docker-compose --profile dev up --build
```

### 3. Debug Docker Logs

If you encounter issues with the Docker containers:

```bash
# View the development container logs
./scripts/debug-docker-dev.sh

# Or manually with Docker Compose
docker-compose --profile dev logs api
```

## Environment Variables

The project uses separate environment files for development and production:

- `.env.development`: Configuration for development mode
- `.env.production`: Configuration for production mode
- `example.env.development`: Template for development environment variables
- `example.env.production`: Template for production environment variables

To set up your environment:
```bash
# For development
cp example.env.development .env.development
# Modify as needed

# For production
cp example.env.production .env.production
# Modify as needed, especially the SECRET_KEY
```

### Available Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `FLASK_ENV` | Application environment | `development` |
| `DEBUG` | Enable auto-reload (development) | `true` in dev, `false` in prod |
| `LOG_LEVEL` | Logging level (debug, info, warning, error, critical) | `debug` in dev, `warning` in prod |
| `PORT` | Port to run the application | `5000` |
| `HOST` | Host to bind to | `0.0.0.0` |
| `SECRET_KEY` | Secret key for sessions/cookies | Required in production |
| `ENABLE_SWAGGER` | Enable Swagger UI | `true` in dev, `false` in prod |
| `CORS_ALLOW_ALL` | Allow CORS from any origin | `true` in dev, `false` in prod |
| `ALLOWED_ORIGINS` | Comma-separated list of allowed origins | Only used in production |

## Accessing the API

After starting the application:

- API Home/Endpoints: http://localhost:5000/
- API Documentation: http://localhost:5000/docs
- Swagger UI: http://localhost:5000/ui/

The home endpoint provides a dynamic listing of all available API endpoints.

## OpenAPI Specification

The API is defined using a modular OpenAPI 3.0 specification:

- `docs/openapi/specification.yaml`: Main entry point
- `docs/openapi/paths/`: API endpoint definitions
- `docs/openapi/components/`: Reusable components (schemas, parameters, responses)

### Combining OpenAPI Files

This project includes a utility to combine the modular OpenAPI files into a single file:

```bash
# Generate a combined YAML file
python scripts/combine_openapi.py docs/openapi/specification.yaml -o combined.yaml

# Output as JSON
python scripts/combine_openapi.py docs/openapi/specification.yaml --json -o combined.json
```

## Troubleshooting

### Connection Issues

If you encounter connection issues when accessing the API:

1. **Port Conflicts**: Ensure that port 5000 (or your configured port) isn't being used by another service:
   ```
   # Check what's using port 5000
   lsof -i :5000
   ```

2. **Docker Logs**: View the container logs for debugging:
   ```
   ./scripts/debug-docker-dev.sh
   ```

3. **Firewall Settings**: Check if your firewall is blocking connections to port 5000.
