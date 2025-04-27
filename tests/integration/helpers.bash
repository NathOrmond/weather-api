#!/usr/bin/env bash

# Common helper functions for BATS integration tests

# ANSI color codes for better output visibility
export GREEN='\033[0;32m'
export YELLOW='\033[1;33m'
export RED='\033[0;31m'
export BLUE='\033[0;34m'
export CYAN='\033[0;36m'
export NC='\033[0m' # No Color

export REQUEST_COUNT=0
export FAILED_REQUESTS=0

check_status_code() {
  local response="$1"
  local expected="$2"
  # Look for the status code in the HTTP/1.x or HTTP/2 status line
  local status_line=$(echo "$response" | grep -E "^HTTP/[0-9]+\.[0-9]+ [0-9]+" | head -n 1)
  local status=$(echo "$status_line" | grep -oE "[0-9]{3}" | head -n 1)
  echo -e "${BLUE}[DEBUG]${NC} HTTP Status Line: $status_line"
  echo -e "${BLUE}[DEBUG]${NC} Extracted Status Code: $status"
  if [ -z "$status" ]; then
    echo -e "${RED}[ASSERTION FAILED]${NC} Failed to extract HTTP status code from response"
    echo -e "${YELLOW}[RESPONSE SNIPPET]${NC}"
    echo "$response" | head -n 10
    if [ "$(echo "$response" | wc -l)" -gt 10 ]; then
      echo -e "${YELLOW}[... response truncated ...]${NC}"
    fi
    FAILED_REQUESTS=$((FAILED_REQUESTS + 1))
    return 1
  fi
  if [ "$status" != "$expected" ]; then
    echo -e "${RED}[ASSERTION FAILED]${NC} Expected status code ${YELLOW}$expected${NC}, got ${RED}$status${NC}"
    echo -e "${YELLOW}[RESPONSE SNIPPET]${NC}"
    echo "$response" | head -n 10
    if [ "$(echo "$response" | wc -l)" -gt 10 ]; then
      echo -e "${YELLOW}[... response truncated ...]${NC}"
    fi
    FAILED_REQUESTS=$((FAILED_REQUESTS + 1))
    return 1
  fi
  echo -e "${GREEN}[STATUS OK]${NC} Received expected status code ${GREEN}$status${NC}"
  return 0
}

# Usage: make_request "GET" "/endpoint" ["request_body"]
make_request() {
  local method="$1"
  local endpoint="$2"
  local data="$3"
  local url="${API_BASE_URL}${endpoint}"
  REQUEST_COUNT=$((REQUEST_COUNT + 1))
  echo -e "\n${BLUE}[REQUEST #$REQUEST_COUNT]${NC} ${CYAN}$method${NC} $url"
  if [ -n "$data" ]; then
    echo -e "${BLUE}[REQUEST BODY]${NC} $data"
  fi
  local start_time=$(date +%s.%N)
  local response
  if [ -n "$data" ]; then
    # If data is provided, add it as JSON payload
    response=$(curl -s -X "$method" "$url" \
      -H "Content-Type: application/json" \
      -d "$data" \
      -i)  
  else
    # Otherwise just make a simple request
    response=$(curl -s -X "$method" "$url" -i)
  fi
  local end_time=$(date +%s.%N)
  local time_taken=$(echo "$end_time - $start_time" | bc)
  local status_line=$(echo "$response" | grep -E "^HTTP/[0-9]+\.[0-9]+ [0-9]+" | head -n 1)
  local status=$(echo "$status_line" | grep -oE "[0-9]{3}" | head -n 1)
  if [ -z "$status" ]; then
    echo -e "${RED}[RESPONSE ERROR]${NC} Could not determine HTTP status code"
  else
    echo -e "${BLUE}[RESPONSE]${NC} Status: $status, Time: ${time_taken}s"
  fi
  echo "$response"
}

# Generate a unique test identifier (useful for creating unique test data)
generate_test_id() {
  local id="test_$(date +%s)_$RANDOM"
  echo -e "${BLUE}[GENERATED ID]${NC} $id"
  echo "$id"
}

# Extract JSON field from response body (skips HTTP headers)
# Usage: extract_json_field "response" "field_name"
extract_json_field() {
  local response="$1"
  local field="$2"
  # Skip HTTP headers by finding the first '{' character
  local value=$(echo "$response" | sed -n '/^{/,$p' | jq -r ".$field")
  echo -e "${BLUE}[EXTRACTED FIELD]${NC} $field = $value"
  echo "$value"
}

# Generate a valid JSON weather report for testing
# Usage: generate_weather_report ["city_name"]
generate_weather_report() {
  local city="${1:-TestCity}"
  local timestamp="$(date -u +"%Y-%m-%dT%H:%M:%SZ")"
  local json='{
    "city": "'"$city"'",
    "temperature": 21.5,
    "condition": "Sunny",
    "timestamp": "'"$timestamp"'"
  }'
  echo -e "${BLUE}[GENERATED WEATHER REPORT]${NC} for city: $city"
  echo "$json"
} 