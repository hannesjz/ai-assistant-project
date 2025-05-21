#!/bin/bash

# Run script for Semantic Search Edition of Ekonomisk Rådgivare
# This script provides a convenient way to run the semantic search application

# Default values
DATA_DIR="./data"
INDEX_DIR=""
SEARCH_QUERY=""
USE_FUZZY=false
USE_SEMANTIC=false
ANALYZE=false
DOCUMENT_TYPE=""
SHOW_CLUSTERS=false
SHOW_ENTITIES=false
TREND_FIELD=""
GROUP_BY="date"
RELATED_TERM=""
OUTPUT_FILE=""

# Function to display usage
function show_usage {
    echo "Usage: $0 [options]"
    echo "Options:"
    echo "  --index DIR       Index files in directory"
    echo "  --search QUERY    Search for documents"
    echo "  --fuzzy           Use fuzzy search"
    echo "  --semantic        Use semantic search"
    echo "  --analyze         Analyze documents"
    echo "  --type TYPE       Filter by document type (invoice, receipt, etc.)"
    echo "  --cluster         Show document clusters"
    echo "  --entities        Show extracted entities"
    echo "  --trends FIELD    Analyze trends in field (e.g., total_amount)"
    echo "  --group-by FIELD  Field to group by for trend analysis (default: date)"
    echo "  --related TERM    Show terms related to input term"
    echo "  --output FILE     Save results to file"
    echo "  --help            Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0 --index ./test_files"
    echo "  $0 --search \"faktura\" --semantic"
    echo "  $0 --search \"belopp\" --type invoice"
    echo "  $0 --cluster"
    echo "  $0 --entities"
    echo "  $0 --related \"faktura\""
    echo "  $0 --trends total_amount --group-by date"
    echo "  $0 --analyze"
    echo "  $0 --search \"faktura\" --output results.txt"
}

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case "$1" in
        --index)
            INDEX_DIR="$2"
            shift 2
            ;;
        --search)
            SEARCH_QUERY="$2"
            shift 2
            ;;
        --fuzzy)
            USE_FUZZY=true
            shift
            ;;
        --semantic)
            USE_SEMANTIC=true
            shift
            ;;
        --analyze)
            ANALYZE=true
            shift
            ;;
        --type)
            DOCUMENT_TYPE="$2"
            shift 2
            ;;
        --cluster)
            SHOW_CLUSTERS=true
            shift
            ;;
        --entities)
            SHOW_ENTITIES=true
            shift
            ;;
        --trends)
            TREND_FIELD="$2"
            shift 2
            ;;
        --group-by)
            GROUP_BY="$2"
            shift 2
            ;;
        --related)
            RELATED_TERM="$2"
            shift 2
            ;;
        --output)
            OUTPUT_FILE="$2"
            shift 2
            ;;
        --help)
            show_usage
            exit 0
            ;;
        *)
            echo "Unknown option: $1"
            show_usage
            exit 1
            ;;
    esac
done

# Build command
CMD="python3 src/main_semantic.py"

# Add options
if [ -n "$INDEX_DIR" ]; then
    CMD="$CMD --index $INDEX_DIR"
fi

if [ -n "$SEARCH_QUERY" ]; then
    CMD="$CMD --search \"$SEARCH_QUERY\""
fi

if [ "$USE_FUZZY" = true ]; then
    CMD="$CMD --fuzzy"
fi

if [ "$USE_SEMANTIC" = true ]; then
    CMD="$CMD --semantic"
fi

if [ "$ANALYZE" = true ]; then
    CMD="$CMD --analyze"
fi

if [ -n "$DOCUMENT_TYPE" ]; then
    CMD="$CMD --type $DOCUMENT_TYPE"
fi

if [ "$SHOW_CLUSTERS" = true ]; then
    CMD="$CMD --cluster"
fi

if [ "$SHOW_ENTITIES" = true ]; then
    CMD="$CMD --entities"
fi

if [ -n "$TREND_FIELD" ]; then
    CMD="$CMD --trends $TREND_FIELD"
fi

if [ -n "$GROUP_BY" ]; then
    CMD="$CMD --group-by $GROUP_BY"
fi

if [ -n "$RELATED_TERM" ]; then
    CMD="$CMD --related \"$RELATED_TERM\""
fi

if [ -n "$OUTPUT_FILE" ]; then
    CMD="$CMD --output $OUTPUT_FILE"
fi

# Run command
echo "Running: $CMD"
eval $CMD