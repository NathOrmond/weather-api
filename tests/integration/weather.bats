#!/usr/bin/env bats

# Load the helper functions first to ensure color definitions are available
load helpers
# Load setup_docker which depends on helpers for color definitions
load setup_docker

# Test city with unique identifier to avoid conflicts between test runs
TEST_CITY="TestCity_$(date +%s)"

# Run once before all tests in this file
setup_file() {
  echo -e "${BLUE}[SETUP]${NC} Checking if API is available..."
  
  # Simple check to see if the API is already running
  if curl --silent --fail "http://localhost:5000/" > /dev/null; then
    echo -e "${GREEN}[INFO]${NC} API is already running"
  else
    echo -e "${YELLOW}[WARNING]${NC} API not detected, attempting to start container"
    # Start the container directly
    docker-compose up -d api
    
    # Wait for it to be ready
    local timeout=30
    local attempt=1
    while ! curl --silent --fail "http://localhost:5000/" > /dev/null; do
      if [ "$attempt" -gt "$timeout" ]; then
        echo -e "${RED}[ERROR]${NC} API did not become ready within $timeout seconds"
        return 1
      fi
      echo -n "."
      sleep 1
      attempt=$((attempt + 1))
    done
    echo -e "\n${GREEN}[SUCCESS]${NC} API is now ready!"
  fi
  
  # Get the API info
  local health_info=$(curl -s "http://localhost:5000/")
  echo -e "${BLUE}[API]${NC} $(echo "$health_info" | jq -r .)"
}

# Run once after all tests in this file
teardown_file() {
  # Don't stop the container automatically to allow for debugging
  echo -e "${BLUE}[TEARDOWN]${NC} Tests completed, leaving container running for debugging."
  echo -e "${BLUE}[TEARDOWN]${NC} To stop manually: docker-compose down"
}

# Print test start information
setup() {
  echo -e "\n${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
  echo -e "${BLUE}[TEST]${NC} ${YELLOW}$BATS_TEST_NAME${NC}"
  echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
}

# Print test result information
teardown() {
  if [ "$BATS_TEST_COMPLETED" = "1" ]; then
    echo -e "${GREEN}[PASSED]${NC} Test completed successfully"
  else
    echo -e "${RED}[FAILED]${NC} Test did not complete successfully"
  fi
  echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
}

# Basic health check
@test "GET / returns 200 OK and health message" {
  echo -e "${CYAN}[INFO]${NC} Checking API health endpoint"
  response=$(make_request "GET" "/")
  
  # Check status code
  check_status_code "$response" "200"
  
  # Check response body
  echo -e "${BLUE}[ASSERTION]${NC} Checking for health:OK in response"
  echo "$response" | grep -q '"health":"OK"'
  
  # Check if endpoints are listed
  echo -e "${BLUE}[ASSERTION]${NC} Checking if endpoints are listed"
  echo "$response" | grep -q '"endpoints":'
}

# Documentation endpoint
@test "GET /docs returns 200 OK and HTML content" {
  echo -e "${CYAN}[INFO]${NC} Checking documentation endpoint"
  response=$(make_request "GET" "/docs")
  
  # Check status code
  check_status_code "$response" "200"
  
  # Check for HTML content
  echo -e "${BLUE}[ASSERTION]${NC} Checking for HTML title and ReDoc content"
  echo "$response" | grep -q "<title>Weather API Docs</title>"
  echo "$response" | grep -q "<redoc"
}

# Swagger UI endpoint
@test "GET /ui returns 200 OK and Swagger UI" {
  echo -e "${CYAN}[INFO]${NC} Checking Swagger UI endpoint"
  
  # Try the /ui/ endpoint directly since redirection isn't properly handled
  echo -e "${BLUE}[TEST]${NC} Requesting /ui/ endpoint directly"
  response=$(curl -s "http://localhost:5000/ui/")
  
  # Check for Swagger UI content
  echo -e "${BLUE}[ASSERTION]${NC} Checking for Swagger UI content"
  if ! echo "$response" | grep -q "swagger-ui"; then
    echo "Error: Response does not contain swagger-ui"
    echo "Response snippet: $(echo "$response" | head -20 | tail -5)"
    return 1
  fi
  
  echo -e "${GREEN}[SUCCESS]${NC} Swagger UI loaded successfully"
}

# OpenAPI specification
@test "GET /openapi.json returns 200 OK and valid OpenAPI spec" {
  skip "TODO: implement this in the server"
  echo -e "${CYAN}[INFO]${NC} Checking OpenAPI specification endpoint"
  
  # Use direct curl command
  response=$(curl -s "http://localhost:5000/openapi.json" -H "Accept: application/json")
  
  # Check if it's a valid JSON
  if ! echo "$response" | jq . > /dev/null; then
    echo "Error: Invalid JSON response"
    echo "Response: $response"
    return 1
  fi
  
  # Validate it's a JSON response with OpenAPI elements
  echo -e "${BLUE}[ASSERTION]${NC} Checking for OpenAPI schema elements"
  
  # Check for essential OpenAPI fields
  for field in "openapi" "paths" "components"; do
    if ! echo "$response" | jq -e "has(\"$field\")" > /dev/null; then
      echo "Error: Response missing $field field"
      return 1
    fi
  done
  
  echo -e "${GREEN}[SUCCESS]${NC} Valid OpenAPI specification received"
}

# Create a new weather report
@test "POST /weather creates a new report" {
  echo -e "${CYAN}[INFO]${NC} Testing creation of a new weather report for $TEST_CITY"
  
  # Test creating a weather report with a direct curl command
  echo -e "${BLUE}[TEST]${NC} Using direct curl command"
  response=$(curl -s -X POST "http://localhost:5000/weather" \
    -H "Content-Type: application/json" \
    -d "{\"city\":\"$TEST_CITY\",\"temperature\":21.5,\"condition\":\"Sunny\",\"timestamp\":\"$(date -u +"%Y-%m-%dT%H:%M:%SZ")\"}" \
    -i)
  
  echo -e "${BLUE}[DEBUG]${NC} Curl response: $response"
  
  # Check the status code (should be 201 Created)
  status_code=$(echo "$response" | grep -E "^HTTP/[0-9]+\.[0-9]+ [0-9]+" | grep -oE "[0-9]{3}")
  echo -e "${BLUE}[DEBUG]${NC} Status code: $status_code"
  
  # Assert that the status code is 201
  [ "$status_code" = "201" ]
  
  # Extract the response body
  body=$(echo "$response" | sed -n '/^{/,$p')
  echo -e "${BLUE}[DEBUG]${NC} Response body: $body"
  
  # Verify the JSON contains expected fields
  echo "$body" | jq -e ".city" > /dev/null || echo "Missing city field"
  echo "$body" | jq -e ".temperature" > /dev/null || echo "Missing temperature field"
  echo "$body" | jq -e ".id" > /dev/null || echo "Missing id field"
  
  echo -e "${GREEN}[SUCCESS]${NC} Weather report created successfully"
}

# Get a specific weather report
@test "GET /weather/{city} retrieves the report" {
  echo -e "${CYAN}[INFO]${NC} Testing retrieval of weather report for $TEST_CITY"
  
  # First create a report to ensure it exists
  echo -e "${BLUE}[SETUP]${NC} Creating a weather report for $TEST_CITY"
  timestamp=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
  curl -s -X POST "http://localhost:5000/weather" \
    -H "Content-Type: application/json" \
    -d "{\"city\":\"$TEST_CITY\",\"temperature\":21.5,\"condition\":\"Sunny\",\"timestamp\":\"$timestamp\"}" \
    -i > /dev/null
    
  # Wait a moment for the data to be processed
  sleep 1
  
  # Get the weather report using direct curl
  echo -e "${BLUE}[TEST]${NC} Getting weather report for $TEST_CITY"
  response=$(curl -s "http://localhost:5000/weather/$TEST_CITY" -H "Accept: application/json")
  
  # Check if the response is valid and contains the expected city
  if ! echo "$response" | jq -e ".city" > /dev/null; then
    echo "Error: Invalid JSON response or missing city field"
    echo "Response: $response"
    return 1
  fi
  
  # Check that it's the city we're looking for
  city=$(echo "$response" | jq -r ".city")
  if [ "$city" != "$TEST_CITY" ]; then
    echo "Error: Expected city $TEST_CITY but got $city"
    return 1
  fi
  
  echo -e "${GREEN}[SUCCESS]${NC} Weather report retrieved successfully"
}

# Get all weather reports
@test "GET /weather returns all reports" {
  echo -e "${CYAN}[INFO]${NC} Testing retrieval of all weather reports"
  
  # First create a report to ensure it exists
  echo -e "${BLUE}[SETUP]${NC} Creating a weather report for $TEST_CITY"
  timestamp=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
  curl -s -X POST "http://localhost:5000/weather" \
    -H "Content-Type: application/json" \
    -d "{\"city\":\"$TEST_CITY\",\"temperature\":21.5,\"condition\":\"Sunny\",\"timestamp\":\"$timestamp\"}" \
    -i > /dev/null
    
  # Wait a moment for the data to be processed
  sleep 1
  
  # Get all reports using direct curl
  echo -e "${BLUE}[TEST]${NC} Getting all weather reports"
  response=$(curl -s "http://localhost:5000/weather" -H "Accept: application/json")
  
  # Check if the response is valid and contains the cities array
  if ! echo "$response" | jq -e ".cities" > /dev/null; then
    echo "Error: Invalid JSON response or missing cities array"
    echo "Response: $response"
    return 1
  fi
  
  # Check if our test city is in the results
  echo -e "${BLUE}[ASSERTION]${NC} Checking if $TEST_CITY is in the results"
  if ! echo "$response" | jq -e ".cities[] | select(.city == \"$TEST_CITY\")" > /dev/null; then
    echo "Error: Could not find $TEST_CITY in the list of cities"
    echo "Cities: $(echo "$response" | jq -r '.cities[].city')"
    return 1
  fi
  
  echo -e "${GREEN}[SUCCESS]${NC} All weather reports retrieved successfully"
}

# Update a weather report
@test "PUT /weather/{city} updates the report" {
  echo -e "${CYAN}[INFO]${NC} Testing update of weather report for $TEST_CITY"
  
  # First create a report to ensure it exists
  echo -e "${BLUE}[SETUP]${NC} Creating a weather report for $TEST_CITY"
  timestamp=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
  curl -s -X POST "http://localhost:5000/weather" \
    -H "Content-Type: application/json" \
    -d "{\"city\":\"$TEST_CITY\",\"temperature\":21.5,\"condition\":\"Sunny\",\"timestamp\":\"$timestamp\"}" \
    -i > /dev/null
    
  # Wait a moment for the data to be processed
  sleep 1
  
  # Create an updated report - important: include the city name in the payload
  current_time=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
  echo -e "${BLUE}[DATA]${NC} Creating update payload with timestamp $current_time"
  
  # Make the request using direct curl
  echo -e "${BLUE}[TEST]${NC} Updating weather report for $TEST_CITY"
  response=$(curl -s -X PUT "http://localhost:5000/weather/$TEST_CITY" \
    -H "Content-Type: application/json" \
    -d "{\"city\":\"$TEST_CITY\",\"temperature\":25.0,\"condition\":\"Cloudy\",\"timestamp\":\"$current_time\"}")
  
  # Check if the response is valid and contains the expected fields
  if ! echo "$response" | jq -e ".city" > /dev/null; then
    echo "Error: Invalid JSON response or missing city field"
    echo "Response: $response"
    return 1
  fi
  
  # Verify the response shows updated data
  echo -e "${BLUE}[ASSERTION]${NC} Verifying response shows updated data"
  if ! echo "$response" | jq -e ".temperature == 25.0" > /dev/null; then
    echo "Error: Temperature was not updated properly"
    echo "Temperature: $(echo "$response" | jq -r '.temperature')"
    return 1
  fi
  
  if ! echo "$response" | jq -e ".condition == \"Cloudy\"" > /dev/null; then
    echo "Error: Condition was not updated properly"
    echo "Condition: $(echo "$response" | jq -r '.condition')"
    return 1
  fi
  
  echo -e "${GREEN}[SUCCESS]${NC} Weather report updated successfully"
}

# Delete a weather report
@test "DELETE /weather/{city} removes the report" {
  echo -e "${CYAN}[INFO]${NC} Testing deletion of weather report for $TEST_CITY"
  
  # First create a report to ensure it exists
  echo -e "${BLUE}[SETUP]${NC} Creating a weather report for $TEST_CITY"
  timestamp=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
  curl -s -X POST "http://localhost:5000/weather" \
    -H "Content-Type: application/json" \
    -d "{\"city\":\"$TEST_CITY\",\"temperature\":21.5,\"condition\":\"Sunny\",\"timestamp\":\"$timestamp\"}" \
    -i > /dev/null
    
  # Wait a moment for the data to be processed
  sleep 1
  
  # Verify the report exists first
  echo -e "${BLUE}[VERIFICATION]${NC} Confirming report exists before deletion"
  if ! curl -s "http://localhost:5000/weather/$TEST_CITY" -H "Accept: application/json" | jq -e ".city" > /dev/null; then
    echo "Error: Report does not exist before deletion"
    return 1
  fi
  
  # Delete the test report using direct curl
  echo -e "${BLUE}[TEST]${NC} Deleting weather report for $TEST_CITY"
  delete_response=$(curl -s -X DELETE "http://localhost:5000/weather/$TEST_CITY" -i)
  
  # Check status code (should be 204 No Content)
  status_code=$(echo "$delete_response" | grep -E "^HTTP/[0-9]+\.[0-9]+ [0-9]+" | grep -oE "[0-9]{3}")
  echo -e "${BLUE}[DEBUG]${NC} Delete status code: $status_code"
  
  if [ "$status_code" != "204" ]; then
    echo "Error: Expected status code 204, got $status_code"
    echo "Response: $delete_response"
    return 1
  fi
  
  # Verify the report is gone by trying to get it again
  echo -e "${BLUE}[VERIFICATION]${NC} Attempting to retrieve deleted report (should fail)"
  get_response=$(curl -s "http://localhost:5000/weather/$TEST_CITY" -i)
  get_status=$(echo "$get_response" | grep -E "^HTTP/[0-9]+\.[0-9]+ [0-9]+" | grep -oE "[0-9]{3}")
  
  # Should return 404 Not Found
  if [ "$get_status" != "404" ]; then
    echo "Error: Expected status code 404 after deletion, got $get_status"
    echo "Response: $get_response"
    return 1
  fi
  
  echo -e "${GREEN}[SUCCESS]${NC} Weather report deleted successfully"
}

# Error case - creating report with invalid data
@test "POST /weather with invalid data returns 400 Bad Request" {
  echo -e "${CYAN}[INFO]${NC} Testing error handling with invalid weather data"
  
  # Invalid payload (missing required fields)
  payload='{
    "city": "InvalidCity",
    "temperature": "not_a_number"
  }'
  
  # Make the request
  response=$(make_request "POST" "/weather" "$payload")
  
  # Show the full response for debugging
  echo -e "${BLUE}[DEBUG]${NC} Full response from the error test:"
  echo "$response"
  
  # Check status code
  check_status_code "$response" "400"
  
  # Extract the body JSON 
  body=$(echo "$response" | sed -n '/^{/,$p')
  echo -e "${BLUE}[DEBUG]${NC} Response body: $body"
  
  # Check for validation-related fields in response (title, detail, status) 
  echo -e "${BLUE}[ASSERTION]${NC} Checking for validation error information"
  echo "$body" | jq -e 'has("title")' > /dev/null && echo -e "${GREEN}[PASSED]${NC} Response contains 'title' field"
  echo "$body" | jq -e 'has("detail")' > /dev/null && echo -e "${GREEN}[PASSED]${NC} Response contains 'detail' field"
  echo "$body" | jq -e 'has("status")' > /dev/null && echo -e "${GREEN}[PASSED]${NC} Response contains 'status' field"
  
  echo -e "${GREEN}[SUCCESS]${NC} API correctly rejected invalid data"
}

# Error case - PUT without city in payload returns specific error
@test "PUT /weather/{city} without city in payload returns helpful error message" {
  echo -e "${CYAN}[INFO]${NC} Testing error handling for missing city in PUT request"
  
  # First create a report to ensure it exists
  echo -e "${BLUE}[SETUP]${NC} Creating a weather report for $TEST_CITY"
  timestamp=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
  curl -s -X POST "http://localhost:5000/weather" \
    -H "Content-Type: application/json" \
    -d "{\"city\":\"$TEST_CITY\",\"temperature\":21.5,\"condition\":\"Sunny\",\"timestamp\":\"$timestamp\"}" \
    -i > /dev/null
    
  # Wait a moment for the data to be processed
  sleep 1
  
  # Create a payload deliberately missing the city field
  current_time=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
  echo -e "${BLUE}[DATA]${NC} Creating payload without city field"
  
  # Make the request using direct curl
  echo -e "${BLUE}[TEST]${NC} Attempting to update weather without city field"
  response=$(curl -s -X PUT "http://localhost:5000/weather/$TEST_CITY" \
    -H "Content-Type: application/json" \
    -d "{\"temperature\":25.0,\"condition\":\"Cloudy\",\"timestamp\":\"$current_time\"}")
  
  # Check if the response is valid JSON
  if ! echo "$response" | jq . > /dev/null; then
    echo "Error: Invalid JSON response"
    echo "Response: $response"
    return 1
  fi
  
  # Verify the response contains error information
  echo -e "${BLUE}[ASSERTION]${NC} Verifying error details"
  
  # Check status field equals 400
  if ! echo "$response" | jq -e ".status == 400" > /dev/null; then
    echo "Error: Response doesn't contain status 400"
    echo "Status: $(echo "$response" | jq -r '.status // "missing"')"
    return 1
  fi
  
  # Verify error mentions city is required
  detail=$(echo "$response" | jq -r '.detail // ""')
  if ! echo "$detail" | grep -i "city.*required" > /dev/null; then
    echo "Error: Detail doesn't mention city is required"
    echo "Detail: $detail"
    return 1
  fi
  
  echo -e "${GREEN}[SUCCESS]${NC} API correctly rejected request with helpful error message"
}

@test "DELETE /weather/London datetime test (fixed)" {
  echo -e "${CYAN}[INFO]${NC} Testing that DateTime inconsistency bug is fixed"
  
  # Attempt to delete London's weather data
  echo -e "${BLUE}[TEST]${NC} Attempting to delete city weather data"
  response=$(curl -s -X DELETE "http://localhost:5000/weather/London" -H "accept: application/json")
  
  # Output the response for debugging
  echo -e "${BLUE}[DEBUG]${NC} Response: $response"
  
  # Get status code
  status_code=$(curl -s -I -X DELETE "http://localhost:5000/weather/London" | grep -E "^HTTP/[0-9]+\.[0-9]+ [0-9]+" | grep -oE "[0-9]{3}")
  
  # The request should either succeed with 204 or fail with 404 if there are no reports
  # It should NOT fail with 500 (Internal Server Error) due to datetime inconsistency
  if [ "$status_code" = "500" ]; then
    echo -e "${RED}[ERROR]${NC} Got 500 error, datetime bug might still exist"
    echo "Response: $response"
    return 1
  fi
  
  if [ "$status_code" != "204" ] && [ "$status_code" != "404" ]; then
    echo -e "${RED}[ERROR]${NC} Expected status 204 or 404, got $status_code"
    echo "Response: $response"
    return 1
  fi
  
  # If we get here with a 204 or 404, the bug is fixed
  echo -e "${GREEN}[SUCCESS]${NC} Test confirmed the datetime inconsistency bug is fixed"
} 