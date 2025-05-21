"""
Enhanced PDF Text Extraction Module with OCR Support

This module provides functionality to extract text from PDF files using multiple methods:
1. Primary method: poppler-utils (pdftotext) for efficient text extraction
2. Secondary method: PyPDF2 for more detailed structure analysis
3. OCR method: pdf2image + pytesseract for image-based and scanned PDFs

Dependencies:
- poppler-utils (system package)
- PyPDF2
- pdf2image
- pytesseract
- PIL (Pillow)
"""

import os
import subprocess
import logging
import tempfile
import re
from typing import Dict, List, Optional, Tuple, Union, Any
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class PDFExtractor:
    """Class for extracting text and metadata from PDF files using multiple methods."""
    
    def __init__(self, use_ocr: bool = True, ocr_language: str = "swe+eng"):
        """
        Initialize the PDF Extractor.
        
        Args:
            use_ocr (bool): Whether to use OCR for scanned documents.
            ocr_language (str): Language(s) to use for OCR, e.g., "swe+eng" for Swedish and English.
        """
        self.use_ocr = use_ocr
        self.ocr_language = ocr_language
        self._check_dependencies()
    
    def _check_dependencies(self) -> None:
        """Check if required dependencies are installed."""
        # Check poppler-utils (pdftotext)
        try:
            subprocess.run(['pdftotext', '-v'], stderr=subprocess.PIPE, stdout=subprocess.PIPE)
            logger.info("poppler-utils (pdftotext) is installed.")
        except FileNotFoundError:
            logger.warning("poppler-utils is not installed. This is required for PDF text extraction.")
            logger.warning("Install with: apt-get install -y poppler-utils")
        
        # Check PyPDF2
        try:
            import PyPDF2
            logger.info(f"PyPDF2 {PyPDF2.__version__} is installed.")
        except ImportError:
            logger.warning("PyPDF2 is not installed. This is required for PDF structure analysis.")
            logger.warning("Install with: pip install PyPDF2")
        
        # Check OCR dependencies if OCR is enabled
        if self.use_ocr:
            try:
                import pdf2image
                logger.info(f"pdf2image {pdf2image.__version__} is installed.")
            except ImportError:
                logger.warning("pdf2image is not installed. This is required for OCR.")
                logger.warning("Install with: pip install pdf2image")
            
            try:
                import pytesseract
                logger.info(f"pytesseract {pytesseract.__version__} is installed.")
            except ImportError:
                logger.warning("pytesseract is not installed. This is required for OCR.")
                logger.warning("Install with: pip install pytesseract")
            
            # Check tesseract-ocr system package
            try:
                result = subprocess.run(['tesseract', '--version'], stdout=subprocess.PIPE, text=True)
                logger.info(f"tesseract-ocr is installed: {result.stdout.split()[0]}")
                
                # Check if the specified language is available
                result = subprocess.run(['tesseract', '--list-langs'], stdout=subprocess.PIPE, text=True)
                available_langs = result.stdout.strip().split('\n')[1:]  # Skip the first line (header)
                
                required_langs = self.ocr_language.split('+')
                missing_langs = [lang for lang in required_langs if lang not in available_langs]
                
                if missing_langs:
                    logger.warning(f"Missing tesseract language data for: {', '.join(missing_langs)}")
                    logger.warning(f"Install with: apt-get install -y tesseract-ocr-{' tesseract-ocr-'.join(missing_langs)}")
                else:
                    logger.info(f"All required tesseract language data is installed: {self.ocr_language}")
            except FileNotFoundError:
                logger.warning("tesseract-ocr is not installed. This is required for OCR.")
                logger.warning("Install with: apt-get install -y tesseract-ocr")
    
    def extract_text(self, pdf_path: str) -> Tuple[str, Dict[str, Any]]:
        """
        Extract text from a PDF file using the best available method.
        
        Args:
            pdf_path (str): Path to the PDF file.
        
        Returns:
            Tuple[str, Dict[str, Any]]: Extracted text and metadata.
        """
        logger.info(f"Extracting text from: {pdf_path}")
        
        # Try pdftotext first (fastest method)
        text = self._extract_with_pdftotext(pdf_path)
        
        # If pdftotext failed or returned very little text, try PyPDF2
        if not text or len(text.strip()) < 100:
            logger.info(f"pdftotext extracted little text, trying PyPDF2: {pdf_path}")
            text = self._extract_with_pypdf2(pdf_path)
        
        # If both methods failed or returned very little text, try OCR if enabled
        if (not text or len(text.strip()) < 100) and self.use_ocr:
            logger.info(f"Standard extraction methods failed, trying OCR: {pdf_path}")
            text = self._extract_with_ocr(pdf_path)
        
        # Extract metadata from the text
        metadata = self._extract_metadata(text, pdf_path)
        
        return text, metadata
    
    def _extract_with_pdftotext(self, pdf_path: str) -> str:
        """
        Extract text from a PDF file using pdftotext.
        
        Args:
            pdf_path (str): Path to the PDF file.
        
        Returns:
            str: Extracted text.
        """
        try:
            with tempfile.NamedTemporaryFile(suffix='.txt') as temp:
                subprocess.run(['pdftotext', '-layout', pdf_path, temp.name], 
                               check=True, stderr=subprocess.PIPE)
                
                with open(temp.name, 'r', errors='ignore') as f:
                    text = f.read()
                
                return text
        except subprocess.CalledProcessError as e:
            logger.error(f"pdftotext failed for {pdf_path}: {e.stderr}")
            return ""
        except Exception as e:
            logger.error(f"Error extracting text with pdftotext: {e}")
            return ""
    
    def _extract_with_pypdf2(self, pdf_path: str) -> str:
        """
        Extract text from a PDF file using PyPDF2.
        
        Args:
            pdf_path (str): Path to the PDF file.
        
        Returns:
            str: Extracted text.
        """
        try:
            import PyPDF2
            
            with open(pdf_path, 'rb') as file:
                reader = PyPDF2.PdfReader(file)
                text = ""
                
                for page_num in range(len(reader.pages)):
                    page = reader.pages[page_num]
                    text += page.extract_text() + "\n\n"
                
                return text
        except Exception as e:
            logger.error(f"Error extracting text with PyPDF2: {e}")
            return ""
    
    def _extract_with_ocr(self, pdf_path: str) -> str:
        """
        Extract text from a PDF file using OCR.
        
        Args:
            pdf_path (str): Path to the PDF file.
        
        Returns:
            str: Extracted text.
        """
        try:
            from pdf2image import convert_from_path
            import pytesseract
            from PIL import Image
            
            # Convert PDF to images
            images = convert_from_path(pdf_path)
            
            # Extract text from each image
            text_parts = []
            for i, image in enumerate(images):
                logger.info(f"Processing page {i+1}/{len(images)} with OCR")
                text = pytesseract.image_to_string(image, lang=self.ocr_language)
                text_parts.append(text)
            
            return "\n\n".join(text_parts)
        except Exception as e:
            logger.error(f"Error extracting text with OCR: {e}")
            return ""
    
    def _extract_metadata(self, text: str, pdf_path: str) -> Dict[str, Any]:
        """
        Extract metadata from the text and filename.
        
        Args:
            text (str): Extracted text from the PDF.
            pdf_path (str): Path to the PDF file.
        
        Returns:
            Dict[str, Any]: Extracted metadata.
        """
        metadata = {
            'filename': os.path.basename(pdf_path),
            'path': pdf_path,
            'size': os.path.getsize(pdf_path),
            'last_modified': os.path.getmtime(pdf_path),
        }
        
        # Extract document type (invoice, receipt, etc.)
        doc_type = self._determine_document_type(text, pdf_path)
        metadata['document_type'] = doc_type
        
        # Extract date
        date = self._extract_date(text, pdf_path)
        if date:
            metadata['date'] = date
        
        # Extract additional metadata based on document type
        if doc_type == 'invoice':
            self._extract_invoice_metadata(text, metadata)
        elif doc_type == 'receipt':
            self._extract_receipt_metadata(text, metadata)
        
        return metadata
    
    def _determine_document_type(self, text: str, pdf_path: str) -> str:
        """
        Determine the type of document based on text content and filename.
        
        Args:
            text (str): Extracted text from the PDF.
            pdf_path (str): Path to the PDF file.
        
        Returns:
            str: Document type ('invoice', 'receipt', 'report', 'other').
        """
        text_lower = text.lower()
        filename_lower = os.path.basename(pdf_path).lower()
        
        # Check for invoice indicators
        invoice_indicators = ['faktura', 'invoice', 'räkning', 'kreditfaktura', 'debitfaktura']
        if any(indicator in text_lower for indicator in invoice_indicators) or \
           any(indicator in filename_lower for indicator in invoice_indicators):
            return 'invoice'
        
        # Check for receipt indicators
        receipt_indicators = ['kvitto', 'receipt', 'kassakvitto', 'köpkvitto']
        if any(indicator in text_lower for indicator in receipt_indicators) or \
           any(indicator in filename_lower for indicator in receipt_indicators):
            return 'receipt'
        
        # Check for report indicators
        report_indicators = ['rapport', 'report', 'analys', 'utredning', 'sammanställning']
        if any(indicator in text_lower for indicator in report_indicators) or \
           any(indicator in filename_lower for indicator in report_indicators):
            return 'report'
        
        # Default to 'other' if no specific type is detected
        return 'other'
    
    def _extract_date(self, text: str, pdf_path: str) -> Optional[str]:
        """
        Extract date from text or filename.
        
        Args:
            text (str): Extracted text from the PDF.
            pdf_path (str): Path to the PDF file.
        
        Returns:
            Optional[str]: Extracted date in ISO format (YYYY-MM-DD) or None if not found.
        """
        # Common date patterns in Swedish documents
        date_patterns = [
            # ISO format: YYYY-MM-DD
            r'(\d{4}-\d{2}-\d{2})',
            # Swedish format: YYYY-MM-DD
            r'(\d{4}-\d{1,2}-\d{1,2})',
            # Alternative format: DD/MM/YYYY
            r'(\d{1,2}/\d{1,2}/\d{4})',
            # Alternative format: DD.MM.YYYY
            r'(\d{1,2}\.\d{1,2}\.\d{4})',
            # Date with month name: DD month YYYY
            r'(\d{1,2}\s+(?:januari|februari|mars|april|maj|juni|juli|augusti|september|oktober|november|december)\s+\d{4})',
            # Date with abbreviated month name: DD mon YYYY
            r'(\d{1,2}\s+(?:jan|feb|mar|apr|maj|jun|jul|aug|sep|okt|nov|dec)\s+\d{4})'
        ]
        
        # Look for dates in the text
        for pattern in date_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            if matches:
                # Return the first match (assuming it's the most relevant date)
                return matches[0]
        
        # If no date found in text, try to extract from filename
        filename = os.path.basename(pdf_path)
        for pattern in date_patterns:
            matches = re.findall(pattern, filename)
            if matches:
                return matches[0]
        
        # No date found
        return None
    
    def _extract_invoice_metadata(self, text: str, metadata: Dict[str, Any]) -> None:
        """
        Extract invoice-specific metadata from text.
        
        Args:
            text (str): Extracted text from the PDF.
            metadata (Dict[str, Any]): Metadata dictionary to update.
        """
        text_lower = text.lower()
        
        # Extract invoice number
        invoice_number_patterns = [
            r'fakturanr\s*\.?\:?\s*(\w+)',
            r'faktura\s*nr\s*\.?\:?\s*(\w+)',
            r'faktura\s*#\s*(\w+)',
            r'invoice\s*number\s*\.?\:?\s*(\w+)',
            r'invoice\s*#\s*(\w+)',
            r'fakturanummer\s*\.?\:?\s*(\w+)'
        ]
        
        for pattern in invoice_number_patterns:
            match = re.search(pattern, text_lower)
            if match:
                metadata['invoice_number'] = match.group(1)
                break
        
        # Extract total amount
        amount_patterns = [
            r'(?:total|summa|belopp|att\s+betala)\s*\:?\s*(\d{1,3}(?:[ \.,]\d{3})*(?:[\.,]\d{2})?)\s*(?:kr|sek|:-)',
            r'(?:total|summa|belopp|att\s+betala)\s*\:?\s*(?:kr|sek)\s*(\d{1,3}(?:[ \.,]\d{3})*(?:[\.,]\d{2})?)',
            r'(?:totalt|totalbelopp)\s*\:?\s*(\d{1,3}(?:[ \.,]\d{3})*(?:[\.,]\d{2})?)\s*(?:kr|sek|:-)'
        ]
        
        for pattern in amount_patterns:
            match = re.search(pattern, text_lower)
            if match:
                # Clean up the amount string (remove spaces, standardize decimal separator)
                amount_str = match.group(1).replace(' ', '').replace('.', '').replace(',', '.')
                try:
                    metadata['total_amount'] = float(amount_str)
                except ValueError:
                    logger.warning(f"Could not convert amount to float: {amount_str}")
                break
        
        # Extract VAT amount
        vat_patterns = [
            r'(?:moms|vat)\s*\:?\s*(\d{1,3}(?:[ \.,]\d{3})*(?:[\.,]\d{2})?)\s*(?:kr|sek|:-)',
            r'(?:moms|vat)\s*\:?\s*(?:kr|sek)\s*(\d{1,3}(?:[ \.,]\d{3})*(?:[\.,]\d{2})?)',
            r'(?:momsbelopp)\s*\:?\s*(\d{1,3}(?:[ \.,]\d{3})*(?:[\.,]\d{2})?)\s*(?:kr|sek|:-)'
        ]
        
        for pattern in vat_patterns:
            match = re.search(pattern, text_lower)
            if match:
                # Clean up the amount string
                vat_str = match.group(1).replace(' ', '').replace('.', '').replace(',', '.')
                try:
                    metadata['vat_amount'] = float(vat_str)
                except ValueError:
                    logger.warning(f"Could not convert VAT amount to float: {vat_str}")
                break
        
        # Extract supplier/vendor
        supplier_patterns = [
            r'(?:leverantör|säljare|från)\s*\:?\s*([A-Za-z0-9åäöÅÄÖ\s]+(?:AB|HB|KB|Inc|Ltd)?)',
            r'(?:supplier|vendor|seller)\s*\:?\s*([A-Za-z0-9åäöÅÄÖ\s]+(?:AB|HB|KB|Inc|Ltd)?)'
        ]
        
        for pattern in supplier_patterns:
            match = re.search(pattern, text_lower)
            if match:
                metadata['supplier'] = match.group(1).strip()
                break
        
        # If no supplier found with patterns, try to extract from the top of the document
        if 'supplier' not in metadata:
            # Take the first non-empty line as a potential supplier name
            lines = [line.strip() for line in text.split('\n') if line.strip()]
            if lines:
                metadata['supplier'] = lines[0]
        
        # Extract due date
        due_date_patterns = [
            r'(?:förfallodag|betalningsdag|due\s+date)\s*\:?\s*(\d{4}-\d{2}-\d{2})',
            r'(?:förfaller|förfallodatum|betalas\s+senast)\s*\:?\s*(\d{4}-\d{2}-\d{2})',
            r'(?:förfaller|förfallodatum|betalas\s+senast)\s*\:?\s*(\d{1,2}/\d{1,2}/\d{4})',
            r'(?:förfaller|förfallodatum|betalas\s+senast)\s*\:?\s*(\d{1,2}\.\d{1,2}\.\d{4})'
        ]
        
        for pattern in due_date_patterns:
            match = re.search(pattern, text_lower)
            if match:
                metadata['due_date'] = match.group(1)
                break
    
    def _extract_receipt_metadata(self, text: str, metadata: Dict[str, Any]) -> None:
        """
        Extract receipt-specific metadata from text.
        
        Args:
            text (str): Extracted text from the PDF.
            metadata (Dict[str, Any]): Metadata dictionary to update.
        """
        text_lower = text.lower()
        
        # Extract receipt number
        receipt_number_patterns = [
            r'kvitto\s*nr\s*\.?\:?\s*(\w+)',
            r'kvitto\s*#\s*(\w+)',
            r'receipt\s*number\s*\.?\:?\s*(\w+)',
            r'receipt\s*#\s*(\w+)',
            r'kvittonummer\s*\.?\:?\s*(\w+)'
        ]
        
        for pattern in receipt_number_patterns:
            match = re.search(pattern, text_lower)
            if match:
                metadata['receipt_number'] = match.group(1)
                break
        
        # Extract total amount (similar to invoice)
        amount_patterns = [
            r'(?:total|summa|belopp|att\s+betala)\s*\:?\s*(\d{1,3}(?:[ \.,]\d{3})*(?:[\.,]\d{2})?)\s*(?:kr|sek|:-)',
            r'(?:total|summa|belopp|att\s+betala)\s*\:?\s*(?:kr|sek)\s*(\d{1,3}(?:[ \.,]\d{3})*(?:[\.,]\d{2})?)',
            r'(?:totalt|totalbelopp)\s*\:?\s*(\d{1,3}(?:[ \.,]\d{3})*(?:[\.,]\d{2})?)\s*(?:kr|sek|:-)'
        ]
        
        for pattern in amount_patterns:
            match = re.search(pattern, text_lower)
            if match:
                # Clean up the amount string
                amount_str = match.group(1).replace(' ', '').replace('.', '').replace(',', '.')
                try:
                    metadata['total_amount'] = float(amount_str)
                except ValueError:
                    logger.warning(f"Could not convert amount to float: {amount_str}")
                break
        
        # Extract store/merchant
        store_patterns = [
            r'(?:butik|affär|store)\s*\:?\s*([A-Za-z0-9åäöÅÄÖ\s]+(?:AB|HB|KB|Inc|Ltd)?)',
            r'(?:merchant|seller)\s*\:?\s*([A-Za-z0-9åäöÅÄÖ\s]+(?:AB|HB|KB|Inc|Ltd)?)'
        ]
        
        for pattern in store_patterns:
            match = re.search(pattern, text_lower)
            if match:
                metadata['store'] = match.group(1).strip()
                break
        
        # If no store found with patterns, try to extract from the top of the document
        if 'store' not in metadata:
            # Take the first non-empty line as a potential store name
            lines = [line.strip() for line in text.split('\n') if line.strip()]
            if lines:
                metadata['store'] = lines[0]
        
        # Extract payment method
        payment_patterns = [
            r'(?:betalningssätt|betalat\s+med)\s*\:?\s*([A-Za-z0-9åäöÅÄÖ\s]+)',
            r'(?:payment\s+method|paid\s+with)\s*\:?\s*([A-Za-z0-9åäöÅÄÖ\s]+)'
        ]
        
        for pattern in payment_patterns:
            match = re.search(pattern, text_lower)
            if match:
                metadata['payment_method'] = match.group(1).strip()
                break
        
        # Check for common payment methods if not found with patterns
        if 'payment_method' not in metadata:
            payment_methods = ['visa', 'mastercard', 'amex', 'american express', 'kontant', 'cash', 'swish', 'klarna']
            for method in payment_methods:
                if method in text_lower:
                    metadata['payment_method'] = method
                    break

# For testing
if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python enhanced_pdf_extractor.py <pdf_file>")
        sys.exit(1)
    
    pdf_path = sys.argv[1]
    extractor = PDFExtractor(use_ocr=True)
    
    text, metadata = extractor.extract_text(pdf_path)
    
    print(f"Extracted {len(text)} characters of text")
    print(f"Metadata: {metadata}")
    
    # Save extracted text to file
    output_path = f"{pdf_path}.txt"
    with open(output_path, 'w') as f:
        f.write(text)
    
    print(f"Saved extracted text to {output_path}")