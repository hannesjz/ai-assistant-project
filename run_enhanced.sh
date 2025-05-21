#!/bin/bash

# Run Enhanced Ekonomisk Rådgivare
# This script demonstrates the usage of the enhanced version with OCR and metadata extraction

# Check if a command is provided
if [ $# -eq 0 ]; then
    echo "Usage: ./run_enhanced.sh [index|search|analyze|visualize]"
    echo ""
    echo "Commands:"
    echo "  index      - Index documents in the test_files directory"
    echo "  search     - Search for documents (optionally provide a search term)"
    echo "  analyze    - Analyze documents (optionally specify a document type)"
    echo "  visualize  - Analyze documents and create visualizations"
    echo ""
    echo "Examples:"
    echo "  ./run_enhanced.sh index"
    echo "  ./run_enhanced.sh search faktura"
    echo "  ./run_enhanced.sh analyze invoice"
    echo "  ./run_enhanced.sh visualize"
    exit 1
fi

# Create data directory if it doesn't exist
mkdir -p data

# Process command
case "$1" in
    index)
        echo "Indexing documents in test_files directory..."
        python3 src/main_enhanced.py --index ./test_files
        ;;
    search)
        if [ -z "$2" ]; then
            echo "Searching for all documents..."
            python3 src/main_enhanced.py --search ""
        else
            echo "Searching for documents matching '$2' with fuzzy search..."
            python3 src/main_enhanced.py --search "$2" --fuzzy
        fi
        ;;
    analyze)
        if [ -z "$2" ]; then
            echo "Analyzing all documents..."
            python3 src/main_enhanced.py --analyze
        else
            echo "Analyzing documents of type '$2'..."
            python3 src/main_enhanced.py --analyze --type "$2"
        fi
        ;;
    visualize)
        echo "Analyzing documents and creating visualizations..."
        python3 src/main_enhanced.py --analyze --visualize
        ;;
    *)
        echo "Unknown command: $1"
        echo "Usage: ./run_enhanced.sh [index|search|analyze|visualize]"
        exit 1
        ;;
esac

echo "Done!"