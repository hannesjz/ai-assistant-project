# Ekonomisk Rådgivare - macOS Setup Guide

This guide will help you set up and run the Ekonomisk Rådgivare (Economic Advisor) application on macOS.

## Quick Start

For the fastest setup, run the provided macOS setup script:

```bash
# Create the setup script
cat > setup_macos.sh << 'EOF'
#!/bin/bash
# Setup Script for Ekonomisk Rådgivare on macOS

echo "========================================================="
echo "   Ekonomisk Rådgivare - macOS Setup Script"
echo "========================================================="
echo

# Install Python dependencies
echo "Installing Python dependencies..."
python3 -m pip install pandas openpyxl PyPDF2 nltk pdf2image pytesseract whoosh reportlab

# Download NLTK data
echo "Downloading NLTK data..."
python3 -c "import nltk; nltk.download('punkt'); nltk.download('stopwords')"

# Check for Homebrew
echo "Checking for system dependencies..."
if ! command -v brew &> /dev/null; then
    echo "Homebrew not found. Do you want to install it? (y/n)"
    read -r install_brew
    if [[ "$install_brew" =~ ^[Yy]$ ]]; then
        /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
    else
        echo "Skipping Homebrew installation. You'll need to install poppler manually."
    fi
fi

# Install poppler if Homebrew is available
if command -v brew &> /dev/null; then
    echo "Installing poppler using Homebrew..."
    brew install poppler
    
    echo "Installing tesseract (optional for OCR)..."
    brew install tesseract tesseract-lang
else
    echo "Please install poppler manually to enable PDF text extraction."
fi

# Create directories
echo "Creating directories..."
mkdir -p data
mkdir -p test_files

# Create test files
echo "Creating test files..."
cat > test_files/test_invoice.txt << 'EOFILE'
FAKTURA

Fakturanummer: 2023-001
Datum: 2023-05-15

FRÅN:
Företag AB
Storgatan 123
123 45 Stockholm
Org.nr: 556123-4567
Tel: 08-123 45 67
E-post: info@foretagab.se

TILL:
Kund AB
Kundvägen 45
987 65 Göteborg
Org.nr: 556789-0123

BETALNINGSINFORMATION:
Bankgiro: 123-4567
Förfallodatum: 2023-06-15
Betalningsvillkor: 30 dagar

BESKRIVNING                ANTAL   PRIS      SUMMA
---------------------------------------------------------
Konsulttjänster            10 h    1 200 kr  12 000 kr
Programvaruutveckling      15 h    1 500 kr  22 500 kr
Projektledning              5 h    1 800 kr   9 000 kr
---------------------------------------------------------
                                   DELSUMMA:  43 500 kr
                                   MOMS 25%:  10 875 kr
                                   TOTALT:    54 375 kr

MEDDELANDE:
Tack för ert förtroende! Vid frågor, kontakta oss på info@foretagab.se.

Betalning ska ske senast på förfallodagen. Vid försenad betalning debiteras dröjsmålsränta enligt räntelagen.
EOFILE

cat > test_files/test_budget.csv << 'EOFILE'
Kategori,Januari,Februari,Mars,April,Maj,Juni,Totalt
Inkomst,35000,35000,35000,37500,37500,37500,217500
Hyra,9500,9500,9500,9500,9500,9500,57000
Mat,4500,4200,4800,4300,4600,4700,27100
Transport,1200,1300,1100,1400,1250,1350,7600
Nöje,2000,2500,1800,2200,2800,3000,14300
Sparande,5000,5000,5000,7000,7000,7000,36000
Övrigt,1500,1800,1600,1700,1900,1600,10100
Totala utgifter,23700,24300,23800,26100,27050,27150,152100
Kvar,11300,10700,11200,11400,10450,10350,65400
EOFILE

# Verify installation
echo "Verifying installation..."
python3 src/main.py

echo
echo "========================================================="
echo "   Setup Complete!"
echo "========================================================="
echo
echo "To index documents:"
echo "  python3 src/main.py --index /path/to/your/documents"
echo
echo "To search for documents:"
echo "  python3 src/main.py --search \"your search query\""
echo
echo "To view statistics:"
echo "  python3 src/main.py"
EOF

# Make it executable
chmod +x setup_macos.sh

# Run the script
./setup_macos.sh
```

## Manual Setup for macOS

If you prefer to set up the system manually, follow these steps:

### 1. Install Python Dependencies

```bash
python3 -m pip install pandas openpyxl PyPDF2 nltk pdf2image pytesseract whoosh reportlab
```

### 2. Download NLTK Data

```bash
python3 -c "import nltk; nltk.download('punkt'); nltk.download('stopwords')"
```

### 3. Install System Dependencies

```bash
# Install Homebrew if not already installed
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Install poppler for PDF text extraction
brew install poppler

# Install tesseract for OCR (optional)
brew install tesseract tesseract-lang
```

### 4. Create Data Directory

```bash
mkdir -p data
```

### 5. Verify Installation

```bash
python3 src/main.py
```

## Troubleshooting

### Common Issues on macOS

1. **Command Not Found: python**: Use `python3` instead of `python` on macOS.

2. **PDF Extraction Issues**: 
   - Check if poppler is installed: `brew list poppler`
   - If not installed: `brew install poppler`

3. **Excel/CSV Extraction Issues**:
   - Check if pandas and openpyxl are installed: `pip3 show pandas openpyxl`
   - For older .xls files, you may need to install xlrd: `pip3 install xlrd`

4. **Permission Issues**:
   - If you get permission errors when installing packages, try using: `python3 -m pip install --user [package]`