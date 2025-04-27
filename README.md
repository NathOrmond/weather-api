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
│   ├── openapi/          # OpenAPI specification files
│   ├── todo-specs/       # Technical specifications for current and future work
│   └── warstories/       # Documentation of bugs and their solutions
├── scripts/              
│   ├── combine_openapi.py  # Utility to combine OpenAPI files
│   ├── restart_docker-dev.sh # Script to restart development containers
│   ├── debug-docker-dev.sh # Script to view development container logs
│   └── unit_tests.sh     # Script to run unit tests
├── tests/
│   ├── unit/             # Unit tests
│   │   ├── repositories/ # Tests for repository layer
│   │   └── ...           # Other unit test modules
│   └── integration/      # Integration tests with BATS
│       ├── helpers.bash      # Helper functions for tests
│       ├── setup_docker.bash # Docker container setup/teardown
│       └── weather.bats      # Tests for weather endpoints
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

## Unit Testing

The project uses `pytest` for unit testing with a modular test structure that mirrors the application's architecture.

### Running Unit Tests

To run all unit tests:

```bash
# Using the convenience script
./scripts/unit_tests.sh

# With verbose output
./scripts/unit_tests.sh -v

# With code coverage report
./scripts/unit_tests.sh -c
```

To run tests for a specific module:

```bash
# Example: Test only the repositories
./scripts/unit_tests.sh -m repositories

# With verbose output
./scripts/unit_tests.sh -v -m repositories

# With code coverage
./scripts/unit_tests.sh -c -m repositories
```

### Unit Test Architecture

The unit tests follow these principles:

1. **Mirror Package Structure**: Tests are organized to mirror the main application structure.
   - `tests/unit/repositories/` contains tests for `api/repositories/` code
   - Each subsequent module should have its own test directory

2. **Independent Tests**: Each test case is independent and doesn't depend on the results of other tests.

3. **Repository Pattern Testing**: Tests for repositories verify both the generic CRUD operations and domain-specific query methods.

4. **Mock External Dependencies**: Tests use unittest.mock to isolate components from their dependencies.

5. **Comprehensive Testing**: Test both successful operations and error cases.

Example structure for a new feature:
```
api/
├── models/
│   └── new_feature.py      # Data model for feature
├── repositories/
│   └── new_feature_repo.py # Repository for feature
├── services/
│   └── new_feature_svc.py  # Service for feature

tests/unit/
├── models/
│   └── test_new_feature.py
├── repositories/
│   └── test_new_feature_repo.py
├── services/
│   └── test_new_feature_svc.py
```

### Custom Test Script

The `scripts/unit_tests.sh` script provides a convenient way to run unit tests with various options:

- `-v, --verbose`: Enables verbose output for detailed test results
- `-c, --coverage`: Generates a code coverage report in HTML format
- `-m, --module MODULE`: Specifies a module within the unit tests directory to test

Coverage reports are generated in the `coverage/html/` directory and can be viewed in a web browser.

## Integration Testing

This project includes an integration test suite using BATS to verify the API endpoints against the running Docker container.

### Prerequisites

Before running the tests, ensure you have the following installed locally:

- **Docker & Docker Compose:** To build and run the application container. ([Install Docker](https://docs.docker.com/get-docker/), [Install Docker Compose](https://docs.docker.com/compose/install/))
- **BATS (Bash Automated Testing System):** The test runner.
  - Installation (macOS with Homebrew): `brew install bats-core`
  - Installation (Ubuntu/Debian): `sudo apt-get update && sudo apt-get install bats`
  - Other methods: See [BATS Installation Guide](https://github.com/bats-core/bats-core#installation)
- **jq:** A command-line JSON processor used for assertions.
  - Installation (macOS with Homebrew): `brew install jq`
  - Installation (Ubuntu/Debian): `sudo apt-get update && sudo apt-get install jq`
  - Other methods: See [jq Download Guide](https://jqlang.github.io/jq/download/)
- **curl:** Used to make HTTP requests. Usually pre-installed on Linux/macOS.

### Running the Tests

1. Navigate to the project's root directory in your terminal.
2. Make sure the necessary dependencies are installed (BATS, jq).
3. Execute the BATS test suite:

```bash
# Run all integration tests
bats tests/integration/

# Or run a specific test file
bats tests/integration/weather.bats
```

The test runner will automatically:
- Start the required Docker containers using the `prod` profile
- Wait for the API to become available
- Execute the tests defined in the .bats files
- Stop and remove the containers when testing is complete

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

## Weather API Features

### Auto-creating Cities

When submitting a weather report for a city that doesn't exist in the system, the API will automatically create the city with default values. This allows users to add reports for any city without first creating the city record.

Example:
```bash
curl -X POST "http://localhost:5000/weather" \
  -H "Content-Type: application/json" \
  -d '{"city":"Manchester","temperature":21.5,"condition":"Sunny","timestamp":"2023-06-01T14:00:00Z"}'
```

### UUID-based IDs

The Weather API uses UUID strings for identifying resources rather than sequential integers. This provides globally unique identifiers with no collision risk, improving scalability.

## War Stories Documentation

The project includes a "warstories" documentation section that captures notable bugs, challenges, and their solutions. These documents serve as both historical records and learning resources for developers.

### Current War Stories
To view these war stories, see the markdown files in the `docs/warstories/` directory.

### Adding New War Stories
When encountering and resolving significant issues, consider documenting them as a war story. A good war story includes:

1. Clear description of the issue and its symptoms
2. Root cause analysis
3. Implemented solution with code examples
4. Verification steps
5. Lessons learned

## Technical Specifications

The project includes a `docs/todo-specs/` directory that contains technical specifications for work being done in the repository and features planned for future development. These specs serve multiple purposes:

1. **Documentation for implemented features**: Detailed explanations of how features were implemented and the reasoning behind technical decisions.

2. **Specifications for future work**: Technical requirements and design documents for features that could be implemented by other developers.

3. **Architectural guidelines**: Standards and patterns to follow when extending the application.

Each specification document typically includes:
- Objectives and requirements
- Technical implementation details
- API design considerations
- Testing requirements
- Dependencies and interactions with other components

Developers should reference these specifications when implementing new features to ensure consistency with the project's design principles.

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

## Recent Changes

- Added automatic city creation when submitting weather reports for new cities
- Fixed timezone handling in datetime comparisons across the application
- Updated OpenAPI schema to use UUID strings instead of integers for IDs
- Added comprehensive documentation of bugs and solutions in the warstories directory

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
