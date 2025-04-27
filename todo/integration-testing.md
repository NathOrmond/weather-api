# Technical Specification: BATS Integration Testing for Weather API

## 1. Introduction

This document specifies the setup and implementation of an integration test suite for the Weather API using BATS (Bash Automated Testing System). The tests will run against the production-like Docker container of the application, interacting with its HTTP endpoints to verify functionality against the API specification.

## 2. Objective

-   Implement an automated integration test suite using BATS.
-   Verify the core functionality of the API endpoints (CRUD operations for weather reports) by making HTTP requests to the running Docker container.
-   Ensure the API conforms to its OpenAPI specification regarding request/response formats and status codes.
-   Integrate the test execution into the development workflow.

## 3. Prerequisites

-   **BATS:** The BATS testing framework must be installed. ([Installation Guide](https://github.com/bats-core/bats-core#installation))
-   **Docker & Docker Compose:** Required to build and run the application container.
-   **`curl`:** Used within BATS tests to make HTTP requests. Usually pre-installed on Linux/macOS.
-   **`jq`:** A command-line JSON processor used to parse and assert JSON responses. ([Installation Guide](https://jqlang.github.io/jq/download/))

## 4. Test Suite Structure

It's recommended to place BATS tests in a dedicated directory:

your-project-root/
├── tests/│   
├── integration/│   
│               ├── setup_docker.bash  # Helper for Docker setup/teardown (optional)
│               │   ├── weather.bats       # Tests for /weather endpoints
│               │   └── helpers.bash       # Common helper functions (optional)
│               └── # other test types (unit, etc) ...
├── api/
├── docs/
├── Dockerfile
├── docker-compose.yml
├── app.py
└── # other project files ...

## 5. Docker Container Management (Setup & Teardown)

BATS provides `setup()` and `teardown()` functions that run before and after each test file (or globally using `setup_file`/`teardown_file`). We will use these to manage the Docker container lifecycle.

**Option 1: Using `setup_file` and `teardown_file` (Recommended)**

Create helper functions (e.g., in `tests/integration/setup_docker.bash` or directly in the `.bats` file's `setup_file`/`teardown_file`).

**Example (`tests/integration/weather.bats`):**

```bash
#!/usr/bin/env bats

# Base URL for the API running in Docker
API_BASE_URL="http://localhost:5000"
# Timeout for health check (seconds)
HEALTH_CHECK_TIMEOUT=30
# Container check interval (seconds)
CHECK_INTERVAL=2

# Function to check if the API is ready
_wait_for_api() {
  local start_time=$(date +%s)
  echo "Waiting for API to be ready at $API_BASE_URL..."
  while true; do
    # Check the health endpoint (/)
    curl --silent --fail "$API_BASE_URL/" > /dev/null && break
    local now=$(date +%s)
    if (( now - start_time >= HEALTH_CHECK_TIMEOUT )); then
      echo "Error: API did not become ready within $HEALTH_CHECK_TIMEOUT seconds."
      # Optional: Dump logs before exiting
      # docker-compose --profile prod logs api || true
      return 1
    fi
    echo -n "."
    sleep $CHECK_INTERVAL
  done
  echo " API is ready."
  return 0
}

# Runs once before all tests in this file
setup_file() {
  echo "Setting up test environment (starting Docker container)..."
  # Build image if necessary (can be done outside tests too)
  # docker-compose --profile prod build --no-cache api || return 1

  # Start container using the 'prod' profile in detached mode
  docker-compose --profile prod up -d api || return 1

  # Wait for the API container to be healthy
  _wait_for_api || return 1
  echo "Setup complete."
}

# Runs once after all tests in this file
teardown_file() {
  echo "Tearing down test environment (stopping Docker container)..."
  # Stop and remove containers defined in the prod profile
  docker-compose --profile prod down -v --remove-orphans || echo "Warning: Docker teardown failed."
  echo "Teardown complete."
}

# --- Your BATS Tests Below ---

@test "GET / returns 200 OK and health message" {
  run curl --silent -X GET "$API_BASE_URL/"
  [ "$status" -eq 0 ] # Check curl exit code
  # Check HTTP status code (requires -w '%{http_code}' in curl, more complex)
  # Or check response body using jq
  echo "$output" | jq -e '.health == "OK"'
  echo "$output" | jq -e '.message == "API docs available at /docs"'
}

@test "GET /docs returns 200 OK and HTML content" {
  run curl --silent -X GET "$API_BASE_URL/docs"
  [ "$status" -eq 0 ]
  # Check for HTML content (e.g., presence of <title> tag)
  echo "$output" | grep -q "<title>Weather API Docs</title>"
}

@test "POST /weather creates a new report" {
  # Define JSON payload
  local payload='{"city": "TestCity", "temperature": 10.5, "condition": "Sunny", "timestamp": "2025-04-27T10:00:00Z"}'

  run curl --silent -X POST "$API_BASE_URL/weather" \
    -H "Content-Type: application/json" \
    -d "$payload"

  [ "$status" -eq 0 ]
  # Check response body includes the created data and has an ID
  echo "$output" | jq -e '.city == "TestCity"'
  echo "$output" | jq -e '.temperature == 10.5'
  echo "$output" | jq -e '.condition == "Sunny"'
  echo "$output" | jq -e 'has("id")'
  # Ideally, also check HTTP status code is 201 (requires more complex curl/parsing)
}

@test "GET /weather/{city} retrieves the created report" {
  # This test depends on the previous POST test succeeding
  # In more complex scenarios, use setup() to create data for each test
  run curl --silent -X GET "$API_BASE_URL/weather/TestCity"

  [ "$status" -eq 0 ]
  echo "$output" | jq -e '.city == "TestCity"'
  echo "$output" | jq -e '.temperature == 10.5'
  echo "$output" | jq -e '.condition == "Sunny"'
}

# Add more tests for GET /weather (summary), PUT /weather/{city}, DELETE /weather/{city}
# Remember to handle potential 404s, 400s etc.

# Example for DELETE (assuming TestCity exists from POST)
@test "DELETE /weather/{city} removes the report" {
  run curl --silent -X DELETE "$API_BASE_URL/weather/TestCity"
  [ "$status" -eq 0 ]
  # Delete should ideally return 204 No Content, check this if possible
  # Verify deletion by trying to GET it again
  run curl --silent -X GET "$API_BASE_URL/weather/TestCity"
  # This subsequent GET should fail (non-zero status) or return a 404 (check body)
  [ "$status" -ne 0 ] # Simple check: curl command failed
  # More robust: check for 404 status code or specific error message in output
}

Option 2: Using setup and teardown (Per Test)This is generally not recommended for integration tests involving Docker containers, as starting/stopping the container for every single test (@test) is extremely slow. Use setup_file/teardown_file instead.6. Writing TestsUse run <command> to execute commands like curl.Check the $status variable (exit code of run): [ "$status" -eq 0 ] for success.Check the $output variable (stdout of run).Use jq with the -e flag (exit code based on boolean result) for easy assertions on JSON content: echo "$output" | jq -e '.key == "value"'.Structure tests logically, often following CRUD operations.Consider edge cases and error responses (404, 400).7. Running the TestsNavigate to your project root directory in the terminal.Execute the BATS tests:# Run a specific test file
bats tests/integration/weather.bats

# Run all .bats files in a directory
bats tests/integration/
8. ConsiderationsTest Data: Tests modifying data (POST, PUT, DELETE) can interfere with each other. Consider strategies like:Unique identifiers per test run.Using setup()/teardown() (if faster setup is possible, e.g., API calls instead of Docker restart) to create/delete test-specific data.Running DELETE tests last.HTTP Status Codes: Reliably checking HTTP status codes in BATS with curl often requires parsing the output differently (e.g., using -w '%{http_code}' -o /dev/null) which makes tests more complex. Checking the response body content is often sufficient for basic verification.Production Profile: Ensure the setup_file uses docker-compose --profile prod up to test the Gunicorn environment, not the Flask development server.Build Step: Decide whether to include docker-compose build in the setup_file or run it separately before executing tests.9. Expected OutcomeA reliable integration test suite that can be run automatically.Increased confidence in the API's functionality and adherence to its contract.Faster feedback during development compared to manual testing.10. README Documentation UpdateThe main project README.md file should be updated to include instructions for running the integration tests. Add a new section similar to the following:## Testing

This project includes an integration test suite using BATS to verify the API endpoints against the running Docker container.

### Prerequisites

Before running the tests, ensure you have the following installed locally:

-   **Docker & Docker Compose:** To build and run the application container. ([Install Docker](https://docs.docker.com/get-docker/), [Install Docker Compose](https://docs.docker.com/compose/install/))
-   **BATS (Bash Automated Testing System):** The test runner.
    -   Installation (macOS with Homebrew): `brew install bats-core`
    -   Installation (Ubuntu/Debian): `sudo apt-get update && sudo apt-get install bats`
    -   Other methods: See [BATS Installation Guide](https://github.com/bats-core/bats-core#installation)
-   **jq:** A command-line JSON processor used for assertions.
    -   Installation (macOS with Homebrew): `brew install jq`
    -   Installation (Ubuntu/Debian): `sudo apt-get update && sudo apt-get install jq`
    -   Other methods: See [jq Download Guide](https://jqlang.github.io/jq/download/)
-   **curl:** Used to make HTTP requests. Usually pre-installed on Linux/macOS.

### Running the Tests

1.  Navigate to the project's root directory in your terminal.
2.  Execute the BATS test suite:

    ```bash
    # Run all integration tests
    bats tests/integration/

    # Or run a specific test file
    bats tests/integration/weather.bats
    ```

The test runner will automatically:
    - Start the required Docker containers using the `prod` profile (`docker-compose --profile prod up -d`).
    - Wait for the API to become available.
    - Execute the tests defined
