#!/usr/bin/env bash

# Import helpers to ensure color definitions are available
# This assumes BATS load helpers runs before load setup_docker
# If running standalone, you can source the helpers file directly
if [ -z "$GREEN" ]; then
    # When running outside BATS or if helpers wasn't loaded yet
    SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
    # shellcheck source=./helpers.bash
    source "${SCRIPT_DIR}/helpers.bash"
fi

export API_BASE_URL="http://localhost:5000"
export HEALTH_CHECK_TIMEOUT=30
export CHECK_INTERVAL=2
export VERBOSE=${VERBOSE:-0}  # Add verbose mode flag

# Set verbose mode for debugging
set_verbose() {
  if [ "$1" == "true" ] || [ "$1" == "1" ]; then
    export VERBOSE=1
    echo -e "${BLUE}[DEBUG]${NC} Verbose mode enabled"
  else
    export VERBOSE=0
  fi
}

wait_for_api() {
  local start_time=$(date +%s)
  echo -e "${BLUE}[SETUP]${NC} Waiting for API to be ready at ${YELLOW}$API_BASE_URL${NC}..."
  local attempt=1
  while true; do
    if curl --silent --fail "$API_BASE_URL/" > /dev/null; then
      break
    fi
    local now=$(date +%s)
    local elapsed=$((now - start_time))
    local remaining=$((HEALTH_CHECK_TIMEOUT - elapsed))
    if (( elapsed >= HEALTH_CHECK_TIMEOUT )); then
      echo -e "\n${RED}[ERROR]${NC} API did not become ready within $HEALTH_CHECK_TIMEOUT seconds."
      echo -e "${YELLOW}[DEBUG]${NC} Showing Docker container logs:"
      docker-compose --profile prod logs api || true
      return 1
    fi
    if (( attempt % 5 == 0 )); then
      echo -e "\n${BLUE}[SETUP]${NC} Still waiting... ($elapsed seconds elapsed, $remaining seconds remaining)"
    else
      echo -n "."
    fi
    sleep $CHECK_INTERVAL
    attempt=$((attempt + 1))
  done
  
  local total_time=$(($(date +%s) - start_time))
  echo -e "\n${GREEN}[SUCCESS]${NC} API is ready after $total_time seconds!"
  
  echo -e "${BLUE}[INFO]${NC} Checking API health..."
  local health_response=$(curl --silent "$API_BASE_URL/")
  
  local api_health=$(echo "$health_response" | jq -r '.health // "Unknown"')
  local api_env=$(echo "$health_response" | jq -r '.environment // "Unknown"')
  echo -e "${GREEN}[API STATUS]${NC} Health: $api_health, Environment: $api_env"
  return 0
}

# Start the Docker container and wait for it to be ready
setup_docker() {
  echo -e "\n${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
  echo -e "${BLUE}[SETUP]${NC} Starting test environment setup at $(date)"
  echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}\n"
  if ! docker info >/dev/null 2>&1; then
    echo -e "${RED}[ERROR]${NC} Docker is not running. Please start Docker and try again."
    return 1
  fi
  echo -e "${BLUE}[SETUP]${NC} Starting Docker container using production profile..."
  if docker ps | grep -q weather-api-container-prod; then
    echo -e "${YELLOW}[WARNING]${NC} Container already running. Stopping and removing..."
    docker-compose --profile prod down -v --remove-orphans
  fi
  if ! docker-compose --profile prod up -d api-prod; then
    echo -e "${RED}[ERROR]${NC} Failed to start Docker container."
    return 1
  fi
  echo -e "${GREEN}[SUCCESS]${NC} Docker container started."
  if ! wait_for_api; then
    echo -e "${RED}[ERROR]${NC} Failed to connect to API."
    return 1
  fi
  echo -e "\n${GREEN}[SUCCESS]${NC} Setup complete at $(date). Ready to run tests!"
  echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
}

teardown_docker() {
  echo -e "\n${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
  echo -e "${BLUE}[TEARDOWN]${NC} Starting cleanup at $(date)"
  echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}\n"
  echo -e "${BLUE}[TEARDOWN]${NC} Stopping and removing Docker containers..."
  if ! docker-compose --profile prod down -v --remove-orphans; then
    echo -e "${YELLOW}[WARNING]${NC} Docker teardown encountered issues. You may need to cleanup manually."
  else
    echo -e "${GREEN}[SUCCESS]${NC} Docker containers stopped and removed."
  fi
  echo -e "\n${GREEN}[SUCCESS]${NC} Teardown complete at $(date)."
  echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
} 