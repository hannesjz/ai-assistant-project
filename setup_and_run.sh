#!/bin/bash
# Setup and Run Script for Ekonomisk Rådgivare
# This script helps set up and run the Ekonomisk Rådgivare application on a RunPod instance

set -e  # Exit on error

# Text formatting
BOLD="\033[1m"
GREEN="\033[0;32m"
YELLOW="\033[0;33m"
RED="\033[0;31m"
RESET="\033[0m"

echo -e "${BOLD}=========================================================${RESET}"
echo -e "${BOLD}   Ekonomisk Rådgivare - Setup and Run Script           ${RESET}"
echo -e "${BOLD}=========================================================${RESET}"
echo

# Function to print section headers
print_section() {
    echo
    echo -e "${BOLD}${1}${RESET}"
    echo -e "${BOLD}-----------------------------------------${RESET}"
}

# Function to check if a command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Check Python version
print_section "Checking Python version"
if command_exists python3; then
    PYTHON_CMD="python3"
elif command_exists python; then
    PYTHON_CMD="python"
else
    echo -e "${RED}Error: Python is not installed.${RESET}"
    exit 1
fi

PYTHON_VERSION=$($PYTHON_CMD --version)
echo -e "Using ${GREEN}$PYTHON_VERSION${RESET}"

# Install Python dependencies
print_section "Installing Python dependencies"
echo "Installing required packages..."
$PYTHON_CMD -m pip install pandas openpyxl PyPDF2 nltk pdf2image pytesseract whoosh

# Download NLTK data
print_section "Downloading NLTK data"
echo "Downloading punkt and stopwords..."
$PYTHON_CMD -c "import nltk; nltk.download('punkt'); nltk.download('stopwords')"

# Install system dependencies
print_section "Installing system dependencies"
if command_exists apt-get; then
    echo "Detected Debian/Ubuntu system"
    echo "Installing poppler-utils and tesseract-ocr..."
    apt-get update && apt-get install -y poppler-utils tesseract-ocr tesseract-ocr-swe
elif command_exists brew; then
    echo "Detected macOS with Homebrew"
    echo "Installing poppler and tesseract..."
    brew install poppler tesseract tesseract-lang
else
    echo -e "${YELLOW}Warning: Could not automatically install system dependencies.${RESET}"
    echo "Please install poppler-utils and tesseract-ocr manually."
fi

# Create data directory
print_section "Setting up project structure"
echo "Creating data directory..."
mkdir -p data

# Run dependency test
print_section "Running dependency test"
echo "Checking if all dependencies are correctly installed..."
$PYTHON_CMD test_dependencies.py

# Check if config.json exists
print_section "Checking configuration"
if [ -f "config.json" ]; then
    echo -e "${GREEN}Configuration file found.${RESET}"
else
    echo -e "${YELLOW}Configuration file not found. Creating default config.json...${RESET}"
    cat > config.json << EOF
{
  "data_dir": "./data",
  "index_type": "sqlite",
  "use_ocr": false,
  "max_files_per_batch": 100,
  "supported_file_types": [".pdf", ".xlsx", ".xls", ".csv"]
}
EOF
    echo -e "${GREEN}Created default config.json${RESET}"
fi

# Display usage instructions
print_section "Usage Instructions"
echo -e "${BOLD}To index documents:${RESET}"
echo -e "  $PYTHON_CMD src/main.py --index /path/to/your/documents"
echo
echo -e "${BOLD}To search for documents:${RESET}"
echo -e "  $PYTHON_CMD src/main.py --search \"your search query\""
echo
echo -e "${BOLD}To view statistics:${RESET}"
echo -e "  $PYTHON_CMD src/main.py"
echo

# Ask if user wants to index a directory now
print_section "Quick Start"
echo -e "Would you like to index a directory now? (y/n)"
read -r response
if [[ "$response" =~ ^([yY][eE][sS]|[yY])$ ]]; then
    echo -e "Enter the path to the directory you want to index:"
    read -r index_path
    if [ -d "$index_path" ]; then
        echo -e "Indexing ${GREEN}$index_path${RESET}..."
        $PYTHON_CMD src/main.py --index "$index_path"
    else
        echo -e "${RED}Error: Directory not found.${RESET}"
    fi
fi

echo
echo -e "${BOLD}=========================================================${RESET}"
echo -e "${BOLD}   Setup Complete!                                      ${RESET}"
echo -e "${BOLD}=========================================================${RESET}"