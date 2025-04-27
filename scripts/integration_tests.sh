#!/bin/bash

# Enable verbose mode for debugging
export VERBOSE=1

# Check if API is running
if ! curl -s http://localhost:5000/ > /dev/null; then
  echo "Starting API container..."
  docker-compose up -d api
  
  # Wait for API to be ready
  echo -n "Waiting for API to start"
  for i in {1..30}; do
    if curl -s http://localhost:5000/ > /dev/null; then
      echo "API is ready"
      break
    fi
    echo -n "."
    sleep 1
    if [ $i -eq 30 ]; then
      echo "API failed to start within 30 seconds"
      exit 1
    fi
  done
fi

# Run the tests
bats tests/integration/weather.bats
