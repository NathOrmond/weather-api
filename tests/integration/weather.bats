#!/usr/bin/env bats

# Load the helper functions first to ensure color definitions are available
load helpers
# Load setup_docker which depends on helpers for color definitions
load setup_docker

# Test city with unique identifier to avoid conflicts between test runs
TEST_CITY="TestCity_$(date +%s)"

# Run once before all tests in this file
setup_file() {
  setup_docker
}

# Run once after all tests in this file
teardown_file() {
  teardown_docker
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
  response=$(make_request "GET" "/ui")
  
  # Check status code
  check_status_code "$response" "200"
  
  # Check for Swagger UI content
  echo -e "${BLUE}[ASSERTION]${NC} Checking for Swagger UI content"
  echo "$response" | grep -q "swagger-ui"
}

# OpenAPI specification
@test "GET /openapi.json returns 200 OK and valid OpenAPI spec" {
  echo -e "${CYAN}[INFO]${NC} Checking OpenAPI specification endpoint"
  response=$(make_request "GET" "/openapi.json")
  
  # Check status code
  check_status_code "$response" "200"
  
  # Validate it's a JSON response with OpenAPI elements
  echo -e "${BLUE}[ASSERTION]${NC} Checking for OpenAPI schema elements"
  echo "$response" | grep -q '"openapi":'
  echo "$response" | grep -q '"paths":'
  echo "$response" | grep -q '"components":'
}

# Create a new weather report
@test "POST /weather creates a new report" {
  echo -e "${CYAN}[INFO]${NC} Testing creation of a new weather report for $TEST_CITY"
  
  # Generate a weather report with our unique test city
  payload=$(generate_weather_report "$TEST_CITY")
  
  # Make the request
  response=$(make_request "POST" "/weather" "$payload")
  
  # Check status code (should be 201 Created)
  check_status_code "$response" "201"
  
  # Verify the response contains the created data
  echo -e "${BLUE}[ASSERTION]${NC} Verifying response content matches submitted data"
  body=$(echo "$response" | sed -n '/^{/,$p')
  echo "$body" | jq -e ".city == \"$TEST_CITY\"" > /dev/null
  echo "$body" | jq -e ".temperature == 21.5" > /dev/null
  echo "$body" | jq -e ".condition == \"Sunny\"" > /dev/null
  echo "$body" | jq -e "has(\"id\")" > /dev/null
  
  echo -e "${GREEN}[SUCCESS]${NC} Weather report created successfully"
}

# Get a specific weather report
@test "GET /weather/{city} retrieves the report" {
  echo -e "${CYAN}[INFO]${NC} Testing retrieval of weather report for $TEST_CITY"
  
  # Get the weather report we created in the previous test
  response=$(make_request "GET" "/weather/$TEST_CITY")
  
  # Check status code
  check_status_code "$response" "200"
  
  # Verify the response contains the expected data
  echo -e "${BLUE}[ASSERTION]${NC} Verifying response contains correct weather data"
  body=$(echo "$response" | sed -n '/^{/,$p')
  echo "$body" | jq -e ".city == \"$TEST_CITY\"" > /dev/null
  echo "$body" | jq -e ".temperature == 21.5" > /dev/null
  echo "$body" | jq -e ".condition == \"Sunny\"" > /dev/null
  
  echo -e "${GREEN}[SUCCESS]${NC} Weather report retrieved successfully"
}

# Get all weather reports
@test "GET /weather returns all reports" {
  echo -e "${CYAN}[INFO]${NC} Testing retrieval of all weather reports"
  
  response=$(make_request "GET" "/weather")
  
  # Check status code
  check_status_code "$response" "200"
  
  # Verify it's a JSON array
  echo -e "${BLUE}[ASSERTION]${NC} Verifying response is a JSON array"
  body=$(echo "$response" | sed -n '/^\[/,$p')
  
  # Check if our test city is in the results
  echo -e "${BLUE}[ASSERTION]${NC} Checking if $TEST_CITY is in the results"
  echo "$body" | jq -e ".[] | select(.city == \"$TEST_CITY\")" > /dev/null
  
  echo -e "${GREEN}[SUCCESS]${NC} All weather reports retrieved successfully"
}

# Update a weather report
@test "PUT /weather/{city} updates the report" {
  echo -e "${CYAN}[INFO]${NC} Testing update of weather report for $TEST_CITY"
  
  # Create an updated report
  current_time=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
  echo -e "${BLUE}[DATA]${NC} Creating update payload with timestamp $current_time"
  
  payload='{
    "temperature": 25.0,
    "condition": "Cloudy",
    "timestamp": "'"$current_time"'"
  }'
  
  # Make the request
  response=$(make_request "PUT" "/weather/$TEST_CITY" "$payload")
  
  # Check status code
  check_status_code "$response" "200"
  
  # Verify the response shows updated data
  echo -e "${BLUE}[ASSERTION]${NC} Verifying response shows updated data"
  body=$(echo "$response" | sed -n '/^{/,$p')
  echo "$body" | jq -e ".city == \"$TEST_CITY\"" > /dev/null
  echo "$body" | jq -e ".temperature == 25.0" > /dev/null
  echo "$body" | jq -e ".condition == \"Cloudy\"" > /dev/null
  
  # Double-check by getting the report again
  echo -e "${BLUE}[VERIFICATION]${NC} Retrieving updated report to confirm changes persisted"
  response=$(make_request "GET" "/weather/$TEST_CITY")
  body=$(echo "$response" | sed -n '/^{/,$p')
  echo "$body" | jq -e ".temperature == 25.0" > /dev/null
  
  echo -e "${GREEN}[SUCCESS]${NC} Weather report updated successfully"
}

# Delete a weather report
@test "DELETE /weather/{city} removes the report" {
  echo -e "${CYAN}[INFO]${NC} Testing deletion of weather report for $TEST_CITY"
  
  # Delete the test report
  response=$(make_request "DELETE" "/weather/$TEST_CITY")
  
  # Check status code (should be 204 No Content)
  check_status_code "$response" "204"
  
  # Verify the report is gone by trying to get it again
  echo -e "${BLUE}[VERIFICATION]${NC} Attempting to retrieve deleted report (should fail)"
  response=$(make_request "GET" "/weather/$TEST_CITY")
  
  # Should return 404 Not Found
  check_status_code "$response" "404"
  
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
  
  # Check status code
  check_status_code "$response" "400"
  
  # Verify error response contains validation error info
  echo -e "${BLUE}[ASSERTION]${NC} Checking for validation error information"
  echo "$response" | grep -q "error"
  echo "$response" | grep -q "validation"
  
  echo -e "${GREEN}[SUCCESS]${NC} API correctly rejected invalid data"
} 