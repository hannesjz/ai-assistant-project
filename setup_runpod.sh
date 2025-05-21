#!/bin/bash
# Setup Script for Ekonomisk Rådgivare on RunPod
# This script creates all necessary files and directories after cloning the repository

set -e  # Exit on error

# Text formatting
BOLD="\033[1m"
GREEN="\033[0;32m"
YELLOW="\033[0;33m"
RED="\033[0;31m"
RESET="\033[0m"

echo -e "${BOLD}=========================================================${RESET}"
echo -e "${BOLD}   Ekonomisk Rådgivare - RunPod Setup Script            ${RESET}"
echo -e "${BOLD}=========================================================${RESET}"
echo

# Function to print section headers
print_section() {
    echo
    echo -e "${BOLD}${1}${RESET}"
    echo -e "${BOLD}-----------------------------------------${RESET}"
}

# Check if we're in the right directory
if [ ! -f "src/main.py" ]; then
    echo -e "${RED}Error: This script must be run from the project root directory.${RESET}"
    echo -e "Please navigate to the directory containing src/main.py"
    exit 1
fi

# Install Python dependencies
print_section "Installing Python dependencies"
echo "Installing required packages..."
pip install pandas openpyxl PyPDF2 nltk pdf2image pytesseract whoosh reportlab

# Download NLTK data
print_section "Downloading NLTK data"
echo "Downloading punkt and stopwords..."
python -c "import nltk; nltk.download('punkt'); nltk.download('stopwords')"

# Install system dependencies
print_section "Installing system dependencies"
if command -v apt-get &> /dev/null; then
    echo "Detected Debian/Ubuntu system"
    echo "Installing poppler-utils and tesseract-ocr..."
    apt-get update && apt-get install -y poppler-utils tesseract-ocr tesseract-ocr-swe
else
    echo -e "${YELLOW}Warning: Could not automatically install system dependencies.${RESET}"
    echo "Please install poppler-utils and tesseract-ocr manually."
fi

# Create necessary directories
print_section "Creating directories"
mkdir -p data
mkdir -p test_files

# Create test files
print_section "Creating test files"

# Create test invoice text file
cat > test_files/test_invoice.txt << 'EOF'
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
EOF
echo -e "${GREEN}Created test_files/test_invoice.txt${RESET}"

# Create test budget CSV file
cat > test_files/test_budget.csv << 'EOF'
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
EOF
echo -e "${GREEN}Created test_files/test_budget.csv${RESET}"

# Create PDF creation script
cat > create_test_pdf.py << 'EOF'
#!/usr/bin/env python3
"""
Create Test PDF Files

This script creates test PDF files from text files for testing the Ekonomisk Rådgivare application.
"""

import os
import sys
from pathlib import Path
import argparse

try:
    from reportlab.lib.pagesizes import A4
    from reportlab.pdfgen import canvas
    from reportlab.lib.units import cm
    from reportlab.pdfbase import pdfmetrics
    from reportlab.pdfbase.ttfonts import TTFont
except ImportError:
    print("Error: reportlab package is not installed.")
    print("Install it with: pip install reportlab")
    sys.exit(1)

def text_to_pdf(text_file, pdf_file):
    """Convert a text file to PDF."""
    # Check if text file exists
    if not os.path.exists(text_file):
        print(f"Error: Text file '{text_file}' not found.")
        return False
    
    # Create directory for PDF file if it doesn't exist
    pdf_dir = os.path.dirname(pdf_file)
    if pdf_dir and not os.path.exists(pdf_dir):
        os.makedirs(pdf_dir)
    
    try:
        # Read text file
        with open(text_file, 'r', encoding='utf-8') as f:
            text_content = f.read()
        
        # Create PDF
        c = canvas.Canvas(pdf_file, pagesize=A4)
        width, height = A4
        
        # Try to use a common font
        try:
            pdfmetrics.registerFont(TTFont('Arial', 'Arial.ttf'))
            font_name = 'Arial'
        except:
            font_name = 'Helvetica'  # Fallback to built-in font
        
        c.setFont(font_name, 12)
        
        # Split text into lines
        lines = text_content.split('\n')
        
        # Calculate text position
        y = height - 2 * cm
        left_margin = 2 * cm
        line_height = 14  # points
        
        # Add each line to the PDF
        for line in lines:
            if y < 2 * cm:  # Start a new page if we're at the bottom
                c.showPage()
                c.setFont(font_name, 12)
                y = height - 2 * cm
            
            c.drawString(left_margin, y, line)
            y -= line_height
        
        # Add metadata
        c.setTitle(os.path.basename(text_file))
        c.setAuthor("Ekonomisk Rådgivare Test Script")
        c.setSubject("Test Document")
        c.setKeywords("test,pdf,ekonomisk,rådgivare")
        
        # Save the PDF
        c.save()
        
        print(f"Created PDF: {pdf_file}")
        return True
    
    except Exception as e:
        print(f"Error creating PDF: {e}")
        return False

def main():
    """Main function."""
    parser = argparse.ArgumentParser(description="Create test PDF files from text files.")
    parser.add_argument("text_file", nargs="?", default="test_files/test_invoice.txt",
                        help="Path to the text file (default: test_files/test_invoice.txt)")
    parser.add_argument("--output", "-o", default=None,
                        help="Output PDF file path (default: same name as text file with .pdf extension)")
    
    args = parser.parse_args()
    
    # Set default output path if not specified
    if args.output is None:
        text_path = Path(args.text_file)
        args.output = str(text_path.with_suffix('.pdf'))
    
    # Convert text to PDF
    success = text_to_pdf(args.text_file, args.output)
    
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())
EOF
chmod +x create_test_pdf.py
echo -e "${GREEN}Created create_test_pdf.py${RESET}"

# Create dependency test script
cat > test_dependencies.py << 'EOF'
#!/usr/bin/env python3
"""
Dependency Test Script for Ekonomisk Rådgivare

This script tests if all required dependencies are correctly installed
and configured for the Ekonomisk Rådgivare application.
"""

import os
import sys
import subprocess
import importlib
import platform
from pathlib import Path

def print_section(title):
    """Print a section title with formatting."""
    print("\n" + "=" * 80)
    print(f" {title} ".center(80, "="))
    print("=" * 80)

def check_python_version():
    """Check if Python version is compatible."""
    print_section("Python Version")
    
    version = sys.version_info
    print(f"Python version: {sys.version}")
    
    if version.major < 3 or (version.major == 3 and version.minor < 10):
        print("❌ Python 3.10 or later is required.")
        return False
    else:
        print("✅ Python version is compatible.")
        return True

def check_python_packages():
    """Check if required Python packages are installed."""
    print_section("Python Packages")
    
    required_packages = {
        "pandas": "Data manipulation",
        "openpyxl": "Excel file handling",
        "PyPDF2": "PDF text extraction",
        "nltk": "Natural language processing",
        "pdf2image": "PDF to image conversion (for OCR)",
        "pytesseract": "OCR functionality",
        "whoosh": "Full-text indexing (optional)"
    }
    
    all_installed = True
    
    for package, description in required_packages.items():
        try:
            module = importlib.import_module(package)
            version = getattr(module, "__version__", "unknown")
            print(f"✅ {package} (version {version}) - {description}")
        except ImportError:
            if package in ["pdf2image", "pytesseract", "whoosh"]:
                print(f"⚠️ {package} - {description} (optional)")
            else:
                print(f"❌ {package} - {description} (required)")
                all_installed = False
    
    return all_installed

def check_nltk_data():
    """Check if required NLTK data is downloaded."""
    print_section("NLTK Data")
    
    try:
        import nltk
        
        required_data = ["punkt", "stopwords"]
        all_downloaded = True
        
        for data in required_data:
            try:
                nltk.data.find(f"tokenizers/{data}")
                print(f"✅ NLTK data '{data}' is downloaded.")
            except LookupError:
                print(f"❌ NLTK data '{data}' is not downloaded.")
                print(f"   Run: python -c \"import nltk; nltk.download('{data}')\"")
                all_downloaded = False
        
        return all_downloaded
    except ImportError:
        print("❌ NLTK is not installed, skipping NLTK data check.")
        return False

def check_system_dependencies():
    """Check if required system dependencies are installed."""
    print_section("System Dependencies")
    
    system = platform.system()
    all_installed = True
    
    # Check for poppler (pdftotext, pdfinfo)
    try:
        subprocess.run(["pdftotext", "-v"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
        print("✅ poppler-utils (pdftotext) is installed.")
    except (subprocess.SubprocessError, FileNotFoundError):
        print("❌ poppler-utils is not installed.")
        if system == "Linux":
            print("   Install with: sudo apt-get install poppler-utils")
        elif system == "Darwin":  # macOS
            print("   Install with: brew install poppler")
        elif system == "Windows":
            print("   Download from: https://github.com/oschwartz10612/poppler-windows/releases/")
        all_installed = False
    
    # Check for tesseract (optional)
    try:
        subprocess.run(["tesseract", "--version"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
        print("✅ tesseract-ocr is installed (optional).")
    except (subprocess.SubprocessError, FileNotFoundError):
        print("⚠️ tesseract-ocr is not installed (optional for OCR functionality).")
        if system == "Linux":
            print("   Install with: sudo apt-get install tesseract-ocr tesseract-ocr-swe")
        elif system == "Darwin":  # macOS
            print("   Install with: brew install tesseract tesseract-lang")
        elif system == "Windows":
            print("   Download from: https://github.com/UB-Mannheim/tesseract/wiki")
    
    return all_installed

def check_project_structure():
    """Check if the project structure is correct."""
    print_section("Project Structure")
    
    required_paths = [
        "src/main.py",
        "src/pdf_extractor/pdf_extractor.py",
        "src/excel_csv_extractor/excel_csv_extractor.py",
        "src/indexing/document_indexer.py",
        "src/utils/file_utils.py",
        "config.json"
    ]
    
    all_exist = True
    
    for path in required_paths:
        if os.path.exists(path):
            print(f"✅ {path} exists.")
        else:
            print(f"❌ {path} does not exist.")
            all_exist = False
    
    # Check data directory
    data_dir = "data"
    if not os.path.exists(data_dir):
        print(f"⚠️ {data_dir} directory does not exist. It will be created when needed.")
        try:
            os.makedirs(data_dir, exist_ok=True)
            print(f"✅ Created {data_dir} directory.")
        except Exception as e:
            print(f"❌ Failed to create {data_dir} directory: {e}")
            all_exist = False
    else:
        print(f"✅ {data_dir} directory exists.")
    
    return all_exist

def main():
    """Run all checks and report results."""
    print_section("Ekonomisk Rådgivare Dependency Test")
    print(f"System: {platform.system()} {platform.release()}")
    print(f"Current directory: {os.getcwd()}")
    
    checks = [
        ("Python Version", check_python_version()),
        ("Python Packages", check_python_packages()),
        ("NLTK Data", check_nltk_data()),
        ("System Dependencies", check_system_dependencies()),
        ("Project Structure", check_project_structure())
    ]
    
    print_section("Summary")
    
    all_passed = True
    for name, result in checks:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} - {name}")
        if not result:
            all_passed = False
    
    if all_passed:
        print("\n✅ All dependency checks passed! The system is ready to use.")
        return 0
    else:
        print("\n⚠️ Some checks failed. Please fix the issues before using the system.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
EOF
chmod +x test_dependencies.py
echo -e "${GREEN}Created test_dependencies.py${RESET}"

# Create test PDF
print_section "Creating test PDF"
python create_test_pdf.py
echo -e "${GREEN}Created test PDF from test invoice${RESET}"

# Run dependency test
print_section "Running dependency test"
python test_dependencies.py

# Display usage instructions
print_section "Usage Instructions"
echo -e "${BOLD}To index documents:${RESET}"
echo -e "  python src/main.py --index /path/to/your/documents"
echo
echo -e "${BOLD}To search for documents:${RESET}"
echo -e "  python src/main.py --search \"your search query\""
echo
echo -e "${BOLD}To view statistics:${RESET}"
echo -e "  python src/main.py"
echo

echo
echo -e "${BOLD}=========================================================${RESET}"
echo -e "${BOLD}   Setup Complete!                                      ${RESET}"
echo -e "${BOLD}=========================================================${RESET}"