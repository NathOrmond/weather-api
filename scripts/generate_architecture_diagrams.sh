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

# Generate dot files with different views and configurations
echo "Generating UML diagrams with Pyreverse..."

# Full detailed class diagram
pyreverse -o dot -p WeatherAPI api -d docs/architecture

# Module-only diagram (simplified package view)
pyreverse -o dot -p WeatherAPI_Modules api -d docs/architecture --filter-mode=ALL --module-names=y --only-classnames

# Models/entities layer diagram
pyreverse -o dot -p Models api/models -d docs/architecture 

# Repositories layer diagram (if exists)
if [ -d "api/repositories" ]; then
    pyreverse -o dot -p Repositories api/repositories -d docs/architecture
fi

# Services layer diagram (if exists)
if [ -d "api/services" ]; then
    pyreverse -o dot -p Services api/services -d docs/architecture
fi

# Check if dot files were generated for the main diagram
if [ ! -f docs/architecture/classes_WeatherAPI.dot ] || [ ! -f docs/architecture/packages_WeatherAPI.dot ]; then
    echo "Error: Pyreverse failed to generate dot files. Check if the 'api' directory exists."
    exit 1
fi

# Create a custom controllers diagram (since they're functions, not classes)
echo "Creating custom controllers diagram..."
cat > docs/architecture/controllers_diagram.dot << 'EOL'
digraph "Controllers" {
	graph [bgcolor="#ffffff", overlap=False, splines=true];
	node [fontname="Helvetica", fontsize=10, shape=record, margin="0.07,0.05"];
	edge [fontname="Helvetica", fontsize=10];
	
	"WeatherController" [
		label="{WeatherController|+ add_weather_report(body)\l+ get_all_city_summaries()\l+ get_city_weather(city)\l+ update_city_weather(city, body)\l+ delete_city_weather(city)\l}"
	];
	
	"WeatherController" -> "WeatherService" [arrowhead=vee, style=dashed];
}
EOL

# Convert dot files to PNG with optimized settings
echo "Converting dot files to PNG using Graphviz..."

# Process each .dot file with improved layouts and sizes
for dot_file in docs/architecture/*.dot; do
    base_name=$(basename "$dot_file" .dot)
    output_file="docs/architecture/${base_name}.png"
    
    # Set different layout algorithms based on diagram type
    if [[ $base_name == *"classes"* ]]; then
        # For class diagrams, use dot layout with reasonable size constraints
        dot -Tpng -Gdpi=150 -Gsize="11,8.5" -Gratio=compress "$dot_file" -o "$output_file"
    else
        # For package diagrams, use fdp layout (force-directed) for better spacing
        fdp -Tpng -Gdpi=150 -Gsize="11,8.5" -Gratio=compress "$dot_file" -o "$output_file"
    fi
    
    # Also generate an SVG version for better scaling in browsers
    dot_file_base="${dot_file%.dot}"
    svg_file="${dot_file_base}.svg"
    dot -Tsvg "$dot_file" -o "$svg_file"
done

# Clean up dot files
echo "Cleaning up dot files..."
rm docs/architecture/*.dot

echo "Done! Diagrams are available in the docs/architecture directory."
echo "View them at: http://localhost:5000/docs/architecture (when the server is running)"
echo "Files generated:"
ls -l docs/architecture/ 