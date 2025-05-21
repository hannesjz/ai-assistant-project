# Ekonomisk Rådgivare - RunPod Setup Guide

This guide will help you set up and run the Ekonomisk Rådgivare (Economic Advisor) application on a RunPod instance.

## Overview

The Ekonomisk Rådgivare is a document processing system that can:
1. Extract text from PDF files
2. Extract structured data from Excel and CSV files
3. Index the extracted content for fast searching
4. Provide a search interface to find relevant information

## Quick Start

For the fastest setup, run the provided setup script:

```bash
# Make the script executable
chmod +x setup.sh

# Run the setup script
./setup.sh
```

This script will:
1. Install all required Python packages
2. Download necessary NLTK data
3. Install system dependencies
4. Create required directories and test files
5. Verify the installation
6. Display usage instructions

If you encounter any issues with the script, you can run the commands manually as described in the Manual Setup section below.

## Manual Setup

If you prefer to set up the system manually, follow these steps:

### 1. Install Python Dependencies

```bash
pip install pandas openpyxl PyPDF2 nltk pdf2image pytesseract whoosh
```

### 2. Download NLTK Data

```bash
python3 -c "import nltk; nltk.download('punkt'); nltk.download('stopwords')"
```

### 3. Install System Dependencies

```bash
apt-get update && apt-get install -y poppler-utils tesseract-ocr tesseract-ocr-swe
```

### 4. Create Data Directory

```bash
mkdir -p data
```

### 5. Run Dependency Test

```bash
python3 test_dependencies.py
```

### 6. Verify Installation

```bash
python src/main.py
```

This should display statistics about the index (which will be empty on first run).

## Testing with Sample Files

The repository includes sample files for testing:

### Create Test PDF

```bash
# Install reportlab if not already installed
pip install reportlab

# Create a test PDF from the sample text file
python3 create_test_pdf.py
```

This will create `test_files/test_invoice.pdf` from the text file.

### Index Test Files

```bash
python3 src/main.py --index test_files
```

### Search Test Files

```bash
python3 src/main.py --search "faktura"
```

## Troubleshooting

### Common Issues

1. **File Not Found Errors**: Make sure you're running commands from the project root directory.

2. **PDF Extraction Issues**:
   - Check if poppler-utils is installed:
     ```bash
     # On Linux/macOS
     pdftotext -v
     
     # On Windows, check that the path is correctly set in PATH
     ```
   - Try running with OCR: Edit `config.json` and set `"use_ocr": true`

3. **Excel/CSV Extraction Issues**:
   - Check if pandas and openpyxl are installed: `pip show pandas openpyxl`
   - For older .xls files, you may need to install xlrd:
     ```bash
     pip install xlrd
     ```
   - For CSV encoding issues, try specifying the encoding in your code

4. **Memory Issues**:
   - Reduce `max_files_per_batch` in `config.json`
   - Process smaller batches of files

### RunPod-Specific Issues

1. **Persistence**: RunPod instances may not persist data between sessions. Consider:
   - Using persistent storage volumes
   - Backing up your indexed data
   - Using Git to version control your code changes

2. **Git Configuration**:
   - Configure Git with your credentials:
     ```bash
     git config --global user.email "your.email@example.com"
     git config --global user.name "Your Name"
     ```
   - Use SSH keys or personal access tokens instead of passwords

3. **Port Forwarding**:
   - If you develop a web interface, use RunPod's port forwarding to access it

## Advanced Configuration

Edit `config.json` to customize the application:

```json
{
  "data_dir": "./data",
  "index_type": "sqlite",
  "use_ocr": false,
  "max_files_per_batch": 100,
  "supported_file_types": [".pdf", ".xlsx", ".xls", ".csv"]
}
```

Options:
- `data_dir`: Directory where indexed data is stored
- `index_type`: Type of index to use ("sqlite" or "whoosh")
- `use_ocr`: Enable OCR for PDF files that don't contain searchable text
- `max_files_per_batch`: Maximum number of files to process in a batch
- `supported_file_types`: List of file types to support

## Project Structure

```
ekonomisk_radgivare/
├── src/
│   ├── pdf_extractor/           # Module for PDF text extraction
│   ├── excel_csv_extractor/     # Module for Excel/CSV data extraction
│   ├── indexing/                # Module for document indexing
│   ├── utils/                   # Helper functions
│   ├── tests/                   # Test modules
│   └── main.py                  # Main application
├── data/                        # Data directory (created automatically)
├── test_files/                  # Sample files for testing
├── config.json                  # Configuration file
├── setup_and_run.sh             # Setup script
├── test_dependencies.py         # Dependency test script
└── create_test_pdf.py           # Script to create test PDFs
```

## Next Steps

1. **Add More Documents**: Index your own documents with `python3 src/main.py --index /path/to/documents`

2. **Explore Search Capabilities**: Try different search queries with `python3 src/main.py --search "your query"`

3. **Extend the System**: Consider adding:
   - A web interface
   - More document types
   - Advanced search features
   - Integration with other systems

## Resources

- [Python Documentation](https://docs.python.org/3/)
- [pandas Documentation](https://pandas.pydata.org/docs/)
- [PyPDF2 Documentation](https://pypdf2.readthedocs.io/)
- [NLTK Documentation](https://www.nltk.org/)
- [RunPod Documentation](https://docs.runpod.io/)