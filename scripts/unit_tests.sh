#!/bin/bash

# run_unit_tests.sh - Script to run specifically unit tests for the Weather API

set -e  # Exit immediately if a command exits with a non-zero status

# Go to project root directory (assuming script is run from anywhere)
cd "$(dirname "${BASH_SOURCE[0]}")/.." || exit 1

echo "Running unit tests for Weather API..."

# Default options
VERBOSE=0
COVERAGE=0
SPECIFIC_MODULE=""

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case "$1" in
        -v|--verbose)
            VERBOSE=1
            shift
            ;;
        -c|--coverage)
            COVERAGE=1
            shift
            ;;
        -m|--module)
            SPECIFIC_MODULE="$2"
            shift 2
            ;;
        *)
            echo "Unknown option: $1"
            echo "Usage: $0 [-v|--verbose] [-c|--coverage] [-m|--module MODULE_NAME]"
            echo "Example: $0 -v -m repositories"
            exit 1
            ;;
    esac
done

# Build pytest command
PYTEST_CMD="python -m pytest"

# Add verbosity if requested
if [[ $VERBOSE -eq 1 ]]; then
    PYTEST_CMD="$PYTEST_CMD -v"
fi

# Add coverage if requested
if [[ $COVERAGE -eq 1 ]]; then
    PYTEST_CMD="$PYTEST_CMD --cov=api --cov-report=html:coverage/html --cov-report=term"
fi

# Add specific module if provided, otherwise test all unit tests
if [[ -n "$SPECIFIC_MODULE" ]]; then
    PYTEST_CMD="$PYTEST_CMD tests/unit/$SPECIFIC_MODULE"
else
    PYTEST_CMD="$PYTEST_CMD tests/unit/"
fi

# Print the command being run
echo "Running: $PYTEST_CMD"

# Run the tests and capture the exit code
eval "$PYTEST_CMD"
TEST_EXIT_CODE=$?

# Check if tests passed and coverage was generated
if [[ $TEST_EXIT_CODE -eq 0 && $COVERAGE -eq 1 ]]; then
    echo "Tests passed! Coverage report generated in coverage/html/"
    echo "Open coverage/html/index.html in your browser to view it"
elif [[ $TEST_EXIT_CODE -eq 0 ]]; then
    echo "All unit tests passed!"
else
    echo "Unit tests failed with exit code $TEST_EXIT_CODE!"
    exit $TEST_EXIT_CODE
fi 