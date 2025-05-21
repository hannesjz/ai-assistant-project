# Enhanced Ekonomisk Rådgivare

This is an enhanced version of the Ekonomisk Rådgivare (Economic Advisor) application with improved features for processing financial documents.

## New Features

1. **OCR for Scanned Documents**
   - Automatically detects when a document is scanned/image-based
   - Uses Tesseract OCR to extract text from images
   - Supports Swedish and English language documents

2. **Metadata Extraction**
   - Automatically identifies document types (invoices, receipts, reports)
   - Extracts key information like dates, amounts, invoice numbers
   - Identifies suppliers, stores, and payment methods

3. **Improved Search**
   - Fuzzy search capability for finding similar terms
   - Filter search by document type or other metadata
   - Relevance-based sorting of search results

4. **Data Analysis and Visualization**
   - Analyze documents by type, date, amount, and supplier
   - Generate statistics about your financial documents
   - Create visualizations of spending patterns

## Requirements

- Python 3.6+
- Tesseract OCR (for OCR functionality)
- Poppler Utils (for PDF processing)
- Python packages:
  - PyPDF2
  - pdf2image
  - pytesseract
  - pandas
  - matplotlib

## Installation

1. Install system dependencies:

   **Ubuntu/Debian:**
   ```bash
   sudo apt-get update
   sudo apt-get install -y tesseract-ocr tesseract-ocr-swe tesseract-ocr-eng poppler-utils
   ```

   **macOS:**
   ```bash
   brew install tesseract tesseract-lang poppler
   ```

2. Install Python dependencies:
   ```bash
   pip install PyPDF2 pdf2image pytesseract pandas matplotlib
   ```

## Usage

### Indexing Documents

To index documents with OCR and metadata extraction:

```bash
python src/main_enhanced.py --index /path/to/documents
```

This will:
- Process all PDF, CSV, Excel, and text files in the directory
- Extract text using OCR for scanned documents
- Extract metadata from documents
- Save everything to the `./data` directory

### Searching Documents

Basic search:
```bash
python src/main_enhanced.py --search "invoice"
```

Fuzzy search (finds similar terms):
```bash
python src/main_enhanced.py --search "faktura" --fuzzy
```

Filter by document type:
```bash
python src/main_enhanced.py --search "belopp" --type invoice
```

### Analyzing Documents

Analyze all documents:
```bash
python src/main_enhanced.py --analyze
```

Analyze specific document type:
```bash
python src/main_enhanced.py --analyze --type receipt
```

Generate visualizations:
```bash
python src/main_enhanced.py --analyze --visualize
```

## Output Files

After processing, the following files will be created in the `./data` directory:

- `*.txt` - Extracted text from documents
- `*.json` - Structured data from CSV/Excel files
- `metadata.json` - Metadata for all processed documents
- `analysis_results.json` - Results of document analysis
- `visualizations/` - Directory containing generated charts and graphs

## Examples

### Example 1: Process a folder of invoices and receipts

```bash
python src/main_enhanced.py --index ~/Documents/Invoices
```

### Example 2: Search for all documents from a specific supplier

```bash
python src/main_enhanced.py --search "ICA" --fuzzy
```

### Example 3: Analyze spending patterns

```bash
python src/main_enhanced.py --analyze --visualize
```

## Troubleshooting

### OCR not working properly

- Make sure Tesseract is installed correctly
- Check that language data is installed for Swedish and English
- Try increasing image quality if possible

### Search not finding expected documents

- Try using the `--fuzzy` option for more flexible matching
- Check that the documents were properly indexed
- Verify the document type if using type filtering

### Visualization errors

- Ensure matplotlib is installed
- Check that you have analyzed documents first
- Make sure the data directory contains processed documents

## Advanced Usage

### Custom Language Support

To use OCR with languages other than Swedish and English, modify the `ocr_language` parameter in the code:

```python
pdf_extractor = PDFExtractor(use_ocr=True, ocr_language="swe+eng+deu")  # Add German
```

### Adding New Document Types

The system automatically detects common document types, but you can extend this by modifying the `_determine_document_type` method in `enhanced_pdf_extractor.py`.

### Customizing Metadata Extraction

To extract additional metadata fields, modify the `_extract_metadata` method and add new extraction functions as needed.