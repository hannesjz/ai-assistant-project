# Simple RunPod Setup Instructions

Here's a simplified approach to set up your project directly on RunPod without needing to clone from GitHub.

## Step 1: Create a Minimal Setup Script

Copy and paste this entire command block into your RunPod terminal:

```bash
cat > setup_minimal.sh << 'EOF'
#!/bin/bash
# Minimal setup script for Ekonomisk Rådgivare on RunPod

echo "========================================================="
echo "   Ekonomisk Rådgivare - Minimal Setup"
echo "========================================================="

# Create project directory structure
mkdir -p my-project
cd my-project
mkdir -p src/pdf_extractor src/excel_csv_extractor src/indexing src/utils src/tests data test_files

# Create config.json
echo '{
  "data_dir": "./data",
  "index_type": "sqlite",
  "use_ocr": false,
  "max_files_per_batch": 100,
  "supported_file_types": [".pdf", ".xlsx", ".xls", ".csv"]
}' > config.json

# Create minimal main.py
echo '
import os
import json
import logging
import argparse

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

def main():
    """Main entry point for the application."""
    parser = argparse.ArgumentParser(description="Ekonomisk Rådgivare - Personal Economic Advisor")
    parser.add_argument("--config", help="Path to configuration file")
    args = parser.parse_args()
    
    # Load config
    config_path = args.config or "config.json"
    try:
        with open(config_path, "r") as f:
            config = json.load(f)
        logger.info(f"Loaded configuration from {config_path}")
    except Exception as e:
        logger.error(f"Failed to load configuration: {e}")
        config = {
            "data_dir": "./data",
            "index_type": "sqlite",
            "use_ocr": False
        }
    
    # Print status
    print(json.dumps({
        "status": "Initialized",
        "config": config,
        "dependencies": {
            "python_packages": ["pandas", "openpyxl", "PyPDF2", "nltk", "pdf2image", "pytesseract", "whoosh"],
            "system_packages": ["poppler-utils", "tesseract-ocr"]
        }
    }, indent=2))

if __name__ == "__main__":
    main()
' > src/main.py

# Create test files
echo 'FAKTURA

Fakturanummer: 2023-001
Datum: 2023-05-15

FRÅN:
Företag AB
Storgatan 123
123 45 Stockholm
' > test_files/test_invoice.txt

echo 'Kategori,Januari,Februari,Mars,April,Maj,Juni,Totalt
Inkomst,35000,35000,35000,37500,37500,37500,217500
Hyra,9500,9500,9500,9500,9500,9500,57000
' > test_files/test_budget.csv

# Create empty __init__.py files
touch src/__init__.py
touch src/pdf_extractor/__init__.py
touch src/excel_csv_extractor/__init__.py
touch src/indexing/__init__.py
touch src/utils/__init__.py
touch src/tests/__init__.py

echo "========================================================="
echo "   Setup Complete!"
echo "========================================================="
echo
echo "Project has been set up in the 'my-project' directory."
echo
echo "To test the application:"
echo "  cd my-project"
echo "  python3 src/main.py"
EOF

chmod +x setup_minimal.sh
./setup_minimal.sh
```

## Step 2: Run the Application

After the setup script completes, you can run the application:

```bash
cd my-project
python3 src/main.py
```

## Step 3: Install Dependencies (if needed)

The dependencies should already be installed on your RunPod instance, but if you need to install them again:

```bash
# Python packages
pip install pandas openpyxl PyPDF2 nltk pdf2image pytesseract whoosh

# NLTK data
python3 -c "import nltk; nltk.download('punkt'); nltk.download('stopwords')"

# System packages
apt-get update && apt-get install -y poppler-utils tesseract-ocr tesseract-ocr-swe
```

## What This Does

This simplified approach:

1. Creates a minimal project structure with all necessary directories
2. Creates a basic config.json file
3. Creates a simple main.py that loads the configuration and displays status
4. Creates sample test files
5. Sets up empty module files

This is a minimal implementation to get you started. You can then develop the full functionality of each module directly on the RunPod instance.

## Troubleshooting

If you encounter any issues:

1. Make sure you're in the correct directory when running commands
2. Check that Python 3 is available with `python3 --version`
3. Verify that the dependencies are installed with `pip list`