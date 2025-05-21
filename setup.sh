#!/bin/bash

# AI Assistant Setup Script
# This script sets up the environment for the AI Assistant with Google Cloud Storage and GitHub integration

set -e  # Exit on error

echo "Setting up AI Assistant..."

# Create virtual environment
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "Installing dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

# Create necessary directories
echo "Creating necessary directories..."
mkdir -p data
mkdir -p models
mkdir -p logs

# Check for Google Cloud SDK
if ! command -v gcloud &> /dev/null; then
    echo "Google Cloud SDK not found. Please install it manually:"
    echo "https://cloud.google.com/sdk/docs/install"
fi

# Check for Git
if ! command -v git &> /dev/null; then
    echo "Git not found. Please install it manually."
fi

# Check for Tesseract OCR
if ! command -v tesseract &> /dev/null; then
    echo "Tesseract OCR not found. Please install it manually:"
    echo "https://github.com/tesseract-ocr/tesseract"
fi

# Check for Poppler (required for pdf2image)
if ! command -v pdftoppm &> /dev/null; then
    echo "Poppler not found. Please install it manually."
    if [[ "$OSTYPE" == "darwin"* ]]; then
        echo "On macOS: brew install poppler"
    elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
        echo "On Ubuntu/Debian: sudo apt-get install poppler-utils"
    fi
fi

# Download spaCy models
echo "Downloading spaCy models..."
python -m spacy download en_core_web_sm
python -m spacy download sv_core_news_sm

# Set up NLTK data
echo "Downloading NLTK data..."
python -c "import nltk; nltk.download('punkt'); nltk.download('stopwords'); nltk.download('wordnet')"

# Make main script executable
chmod +x src/ai_assistant/main.py

echo "Setup complete!"
echo "To activate the environment, run: source venv/bin/activate"
echo "To run the AI Assistant, run: python src/ai_assistant/main.py --help"