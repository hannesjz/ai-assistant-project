# Ultra Simple RunPod Setup

Here's an ultra-simple approach to set up your project on RunPod. Run each command separately:

## Step 1: Create the project structure

```bash
# Create project directory and navigate to it
mkdir -p my-project
cd my-project

# Create directory structure
mkdir -p src/pdf_extractor
mkdir -p src/excel_csv_extractor
mkdir -p src/indexing
mkdir -p src/utils
mkdir -p src/tests
mkdir -p data
mkdir -p test_files

# Create empty __init__.py files
touch src/__init__.py
touch src/pdf_extractor/__init__.py
touch src/excel_csv_extractor/__init__.py
touch src/indexing/__init__.py
touch src/utils/__init__.py
touch src/tests/__init__.py
```

## Step 2: Create config.json

```bash
cat > config.json << 'EOF'
{
  "data_dir": "./data",
  "index_type": "sqlite",
  "use_ocr": false,
  "max_files_per_batch": 100,
  "supported_file_types": [".pdf", ".xlsx", ".xls", ".csv"]
}
EOF
```

## Step 3: Create a simple main.py

```bash
cat > src/main.py << 'EOF'
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
EOF
```

## Step 4: Create test files

```bash
cat > test_files/test_invoice.txt << 'EOF'
FAKTURA

Fakturanummer: 2023-001
Datum: 2023-05-15

FRÅN:
Företag AB
Storgatan 123
123 45 Stockholm
EOF

cat > test_files/test_budget.csv << 'EOF'
Kategori,Januari,Februari,Mars,April,Maj,Juni,Totalt
Inkomst,35000,35000,35000,37500,37500,37500,217500
Hyra,9500,9500,9500,9500,9500,9500,57000
EOF
```

## Step 5: Create minimal module implementations

```bash
# PDF Extractor
cat > src/pdf_extractor/pdf_extractor.py << 'EOF'
import logging

logger = logging.getLogger(__name__)

class PDFExtractor:
    def __init__(self, use_ocr=False):
        self.use_ocr = use_ocr
        logger.info("PDF Extractor initialized")
EOF

# Excel/CSV Extractor
cat > src/excel_csv_extractor/excel_csv_extractor.py << 'EOF'
import logging

logger = logging.getLogger(__name__)

class ExcelCSVExtractor:
    def __init__(self):
        logger.info("Excel/CSV Extractor initialized")
EOF

# Document Indexer
cat > src/indexing/document_indexer.py << 'EOF'
import os
import logging

logger = logging.getLogger(__name__)

class DocumentIndexer:
    def __init__(self, index_dir="data"):
        self.index_dir = index_dir
        os.makedirs(index_dir, exist_ok=True)
        logger.info(f"Document Indexer initialized with index directory: {index_dir}")
EOF

# File Utils
cat > src/utils/file_utils.py << 'EOF'
import os
import logging

logger = logging.getLogger(__name__)

def create_directory_if_not_exists(directory_path):
    if not os.path.exists(directory_path):
        os.makedirs(directory_path)
        logger.info(f"Created directory: {directory_path}")
    return True
EOF
```

## Step 6: Run the application

```bash
python3 src/main.py
```

## Troubleshooting

If you encounter any issues:

1. Make sure you're in the correct directory when running commands
2. Check that Python 3 is available with `python3 --version`
3. Verify that the dependencies are installed with `pip list`

The dependencies should already be installed on your RunPod instance, but if you need to install them again:

```bash
# Python packages
pip install pandas openpyxl PyPDF2 nltk pdf2image pytesseract whoosh

# NLTK data
python3 -c "import nltk; nltk.download('punkt'); nltk.download('stopwords')"

# System packages
apt-get update && apt-get install -y poppler-utils tesseract-ocr tesseract-ocr-swe