#!/bin/bash

# Skript för att installera beroenden på macOS
echo "Installerar beroenden för dokumentprocessorn på macOS..."

# Kontrollera om Homebrew är installerat
if ! command -v brew &> /dev/null; then
    echo "Homebrew är inte installerat. Installerar Homebrew..."
    /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
    
    # Lägg till Homebrew i PATH om det inte redan finns
    if [[ ":$PATH:" != *":/opt/homebrew/bin:"* ]]; then
        echo 'eval "$(/opt/homebrew/bin/brew shellenv)"' >> ~/.zprofile
        eval "$(/opt/homebrew/bin/brew shellenv)"
    fi
    
    echo "Homebrew har installerats."
else
    echo "Homebrew är redan installerat."
fi

# Kontrollera om Python 3 är installerat
PYTHON_CMD=""
if command -v python3 &> /dev/null; then
    PYTHON_CMD="python3"
    echo "Python 3 är redan installerat."
elif command -v python &> /dev/null; then
    # Kontrollera om python är version 3
    PYTHON_VERSION=$(python --version 2>&1 | awk '{print $2}' | cut -d. -f1)
    if [ "$PYTHON_VERSION" -eq 3 ]; then
        PYTHON_CMD="python"
        echo "Python 3 är redan installerat som 'python'."
    else
        echo "Python $PYTHON_VERSION är installerat, men vi behöver Python 3. Installerar Python 3..."
        brew install python3
        PYTHON_CMD="python3"
    fi
else
    echo "Python är inte installerat. Installerar Python 3..."
    brew install python3
    PYTHON_CMD="python3"
fi

# Installera poppler (för pdftotext)
echo "Installerar poppler..."
brew install poppler

# Installera tesseract med svenskt språkpaket
echo "Installerar tesseract med svenskt språkpaket..."
brew install tesseract
brew install tesseract-lang

# Installera Python-beroenden
echo "Installerar Python-beroenden med $PYTHON_CMD..."
$PYTHON_CMD -m pip install --upgrade pip
$PYTHON_CMD -m pip install -r requirements.txt

echo "Installation klar! Du kan nu köra dokumentprocessorn."