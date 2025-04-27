#!/bin/bash

echo "Checking for required dependencies..."
if ! command -v pyreverse &> /dev/null; then
    echo "pyreverse not found! Installing pylint..."
    pip install pylint
fi

if ! command -v dot &> /dev/null; then
    echo "dot (Graphviz) not found! Please install Graphviz:"
    echo "  - Mac: brew install graphviz"
    echo "  - Ubuntu/Debian: sudo apt-get install graphviz"
    echo "  - Windows: Download from https://graphviz.org/download/"
    exit 1
fi

# Create output directory if it doesn't exist
echo "Creating output directory..."
mkdir -p docs/architecture

# Generate dot files
echo "Generating UML diagrams with Pyreverse..."
pyreverse -o dot -p WeatherAPI api -d docs/architecture

# Check if dot files were generated
if [ ! -f docs/architecture/classes_WeatherAPI.dot ] || [ ! -f docs/architecture/packages_WeatherAPI.dot ]; then
    echo "Error: Pyreverse failed to generate dot files. Check if the 'api' directory exists."
    exit 1
fi

# Convert dot files to PNG
echo "Converting dot files to PNG using Graphviz..."
dot -Tpng docs/architecture/classes_WeatherAPI.dot -o docs/architecture/classes.png
dot -Tpng docs/architecture/packages_WeatherAPI.dot -o docs/architecture/packages.png

# Check if PNG files were generated
if [ ! -f docs/architecture/classes.png ] || [ ! -f docs/architecture/packages.png ]; then
    echo "Error: Graphviz failed to generate PNG files."
    exit 1
fi

# Clean up dot files
echo "Cleaning up dot files..."
rm docs/architecture/*.dot

echo "Done! Diagrams are available in the docs/architecture directory."
echo "View them at: http://localhost:5000/docs/architecture (when the server is running)"
echo "Files generated:"
ls -l docs/architecture/ 