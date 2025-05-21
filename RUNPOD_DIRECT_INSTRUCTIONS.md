# RunPod Direct Setup Instructions

Since you're having issues with GitHub authentication on RunPod, here's how to set up the project directly on your RunPod instance without cloning from GitHub.

## Step 1: Create the Setup Script on RunPod

Connect to your RunPod instance via SSH and create the setup script directly:

```bash
# Create the setup script
cat > setup_direct.sh << 'EOF'
#!/bin/bash
# Direct Setup Script for Ekonomisk Rådgivare on RunPod

echo "========================================================="
echo "   Ekonomisk Rådgivare - RunPod Direct Setup"
echo "========================================================="
echo

# Create project directory
echo "Creating project directory structure..."
mkdir -p my-project-name
cd my-project-name

# Create source directories
mkdir -p src/pdf_extractor
mkdir -p src/excel_csv_extractor
mkdir -p src/indexing
mkdir -p src/utils
mkdir -p src/tests
mkdir -p data
mkdir -p test_files

# Install dependencies
echo "Installing Python dependencies..."
pip install pandas openpyxl PyPDF2 nltk pdf2image pytesseract whoosh reportlab

# Download NLTK data
echo "Downloading NLTK data..."
python3 -c "import nltk; nltk.download('punkt'); nltk.download('stopwords')"

# Install system dependencies
echo "Installing system dependencies..."
apt-get update && apt-get install -y poppler-utils tesseract-ocr tesseract-ocr-swe

# Create config.json
echo "Creating configuration file..."
cat > config.json << 'EOFCONFIG'
{
  "data_dir": "./data",
  "index_type": "sqlite",
  "use_ocr": false,
  "max_files_per_batch": 100,
  "supported_file_types": [".pdf", ".xlsx", ".xls", ".csv"]
}
EOFCONFIG

# Create test files
echo "Creating test files..."
cat > test_files/test_invoice.txt << 'EOFINVOICE'
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
EOFINVOICE

cat > test_files/test_budget.csv << 'EOFBUDGET'
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
EOFBUDGET

# Create __init__.py files
echo "Creating module initialization files..."
touch src/__init__.py
touch src/pdf_extractor/__init__.py
touch src/excel_csv_extractor/__init__.py
touch src/indexing/__init__.py
touch src/utils/__init__.py
touch src/tests/__init__.py

# Create minimal implementation of required modules
echo "Creating minimal implementation of required modules..."

# File Utils (create first as other modules depend on it)
cat > src/utils/file_utils.py << 'EOFUTILS'
"""
Utility functions for file operations (Minimal Implementation)
"""
import os
import logging

logger = logging.getLogger(__name__)

def list_files_by_type(directory_path, file_types=None, recursive=True):
    """List files in a directory, grouped by file type."""
    result = {}
    if file_types:
        for file_type in file_types:
            result[file_type] = []
    return result

def get_file_metadata(file_path):
    """Get metadata for a file."""
    return {
        'file_path': file_path,
        'file_name': os.path.basename(file_path)
    }

def create_directory_if_not_exists(directory_path):
    """Create a directory if it doesn't exist."""
    if not os.path.exists(directory_path):
        os.makedirs(directory_path)
        logger.info(f"Created directory: {directory_path}")
    return True
EOFUTILS

# PDF Extractor
cat > src/pdf_extractor/pdf_extractor.py << 'EOFPDF'
"""
PDF Text Extraction Module (Minimal Implementation)
"""
import logging

logger = logging.getLogger(__name__)

class PDFExtractor:
    """Class for extracting text from PDF files."""
    
    def __init__(self, use_ocr=False):
        """Initialize the PDF Extractor."""
        self.use_ocr = use_ocr
        logger.info("PDF Extractor initialized")
EOFPDF

# Excel/CSV Extractor
cat > src/excel_csv_extractor/excel_csv_extractor.py << 'EOFEXCEL'
"""
Excel and CSV Data Extraction Module (Minimal Implementation)
"""
import logging

logger = logging.getLogger(__name__)

class ExcelCSVExtractor:
    """Class for extracting data from Excel and CSV files."""
    
    def __init__(self):
        """Initialize the Excel and CSV Extractor."""
        logger.info("Excel/CSV Extractor initialized")
EOFEXCEL

# Document Indexer
cat > src/indexing/document_indexer.py << 'EOFINDEX'
"""
Document Indexing Module (Minimal Implementation)
"""
import os
import logging

logger = logging.getLogger(__name__)

class DocumentIndexer:
    """Class for indexing and searching documents."""
    
    def __init__(self, index_dir="data"):
        """Initialize the Document Indexer."""
        self.index_dir = index_dir
        os.makedirs(index_dir, exist_ok=True)
        logger.info(f"Document Indexer initialized with index directory: {index_dir}")
EOFINDEX

# Create a simple test
cat > src/tests/test_file_integration.py << 'EOFTEST'
"""
Integration test for file processing
"""
import os
import sys
import logging

# Add parent directory to path to import modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from src.pdf_extractor.pdf_extractor import PDFExtractor
from src.excel_csv_extractor.excel_csv_extractor import ExcelCSVExtractor

def test_extractors():
    """Test that extractors can be initialized."""
    pdf_extractor = PDFExtractor()
    excel_csv_extractor = ExcelCSVExtractor()
    print("Extractors initialized successfully!")
    return True

if __name__ == "__main__":
    test_extractors()
EOFTEST

# Create main.py
echo "Creating main application file..."
cat > src/main.py << 'EOFMAIN'
"""
Main application module for the Economic Advisor

This module integrates all components and provides the main application functionality:
1. File discovery and processing
2. Document indexing and search
3. Knowledge integration
4. User interface
"""

import os
import sys
import logging
import json
import argparse
from pathlib import Path

# Add parent directory to path to import modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.pdf_extractor.pdf_extractor import PDFExtractor
from src.excel_csv_extractor.excel_csv_extractor import ExcelCSVExtractor
from src.indexing.document_indexer import DocumentIndexer
from src.utils.file_utils import list_files_by_type, get_file_metadata, create_directory_if_not_exists

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("ekonomisk_radgivare.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class EkonomiskRadgivare:
    """Main application class for the Economic Advisor."""
    
    def __init__(self, config_path=None):
        """
        Initialize the Economic Advisor.
        
        Args:
            config_path (str): Path to configuration file.
        """
        # Load configuration
        self.config = self._load_config(config_path)
        
        # Create data directory
        data_dir = self.config.get('data_dir', './data')
        create_directory_if_not_exists(data_dir)
        
        # Initialize components
        self.pdf_extractor = PDFExtractor(use_ocr=self.config.get('use_ocr', False))
        self.excel_csv_extractor = ExcelCSVExtractor()
        
        # Initialize indexer
        index_dir = os.path.join(data_dir, "index")
        self.indexer = DocumentIndexer(index_dir=index_dir)
        
        logger.info("Initialized Ekonomisk Radgivare")
    
    def _load_config(self, config_path):
        """
        Load configuration from file or use defaults.
        
        Args:
            config_path (str): Path to configuration file.
        
        Returns:
            dict: Configuration dictionary.
        """
        default_config = {
            'data_dir': './data',
            'index_type': 'sqlite',
            'use_ocr': False,
            'max_files_per_batch': 100,
            'supported_file_types': ['.pdf', '.xlsx', '.xls', '.csv']
        }
        
        if not config_path or not os.path.exists(config_path):
            logger.info("Using default configuration")
            return default_config
        
        try:
            with open(config_path, 'r') as f:
                config = json.load(f)
            
            # Merge with defaults
            for key, value in default_config.items():
                if key not in config:
                    config[key] = value
            
            logger.info(f"Loaded configuration from {config_path}")
            return config
        except Exception as e:
            logger.error(f"Failed to load configuration from {config_path}: {e}")
            return default_config
    
    def get_stats(self):
        """
        Get statistics about the index.
        
        Returns:
            dict: Statistics about the index.
        """
        return {
            "status": "Initialized",
            "config": self.config
        }

def main():
    """Main entry point for the application."""
    parser = argparse.ArgumentParser(description="Ekonomisk Radgivare - Personal Economic Advisor")
    parser.add_argument("--config", help="Path to configuration file")
    parser.add_argument("--index", help="Index files in directory")
    parser.add_argument("--search", help="Search for documents")
    parser.add_argument("--limit", type=int, default=10, help="Maximum number of search results")
    
    args = parser.parse_args()
    
    # Initialize application
    app = EkonomiskRadgivare(args.config)
    
    # If no action specified, print stats
    if not args.index and not args.search:
        stats = app.get_stats()
        print(json.dumps(stats, indent=2, default=str))

if __name__ == "__main__":
    main()
EOFMAIN

echo
echo "========================================================="
echo "   Setup Complete!"
echo "========================================================="
echo
echo "Project has been set up in the 'my-project-name' directory."
echo
echo "To test the application:"
echo "  cd my-project-name"
echo "  python3 src/main.py"
echo
echo "To run the test:"
echo "  python3 src/tests/test_file_integration.py"
echo
echo "This is a minimal implementation to get you started."
echo "You can now develop the full functionality of each module."
EOF

# Make the script executable
chmod +x setup_direct.sh
```

## Step 2: Run the Setup Script

```bash
./setup_direct.sh
```

This script will:
1. Create the project directory structure
2. Install all required Python packages
3. Download necessary NLTK data
4. Install system dependencies (poppler-utils, tesseract-ocr)
5. Create configuration files
6. Create test files
7. Create minimal implementations of all required modules

## Step 3: Test the Installation

After the setup script completes, you can test the installation:

```bash
cd my-project-name
python3 src/main.py
```

You should see output showing the application has been initialized with the default configuration.

## Step 4: Run the Integration Test

```bash
python3 src/tests/test_file_integration.py
```

This should output "Extractors initialized successfully!"

## Next Steps

This setup provides a minimal implementation to get you started. You can now:

1. Develop the full functionality of each module
2. Add more test files
3. Implement the search functionality
4. Create a web interface

## Troubleshooting

If you encounter any issues:

1. **File Permissions**: Make sure all files have the correct permissions
   ```bash
   chmod -R 755 my-project-name
   ```

2. **Python Path**: If you get import errors, check that the Python path is set correctly
   ```bash
   export PYTHONPATH=$PYTHONPATH:/path/to/my-project-name
   ```

3. **Dependencies**: Verify all dependencies are installed
   ```bash
   pip list | grep -E 'pandas|openpyxl|PyPDF2|nltk|pdf2image|pytesseract|whoosh'