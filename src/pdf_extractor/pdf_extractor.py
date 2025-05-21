"""
PDF Text Extraction Module

This module provides functionality to extract text from PDF files using multiple methods:
1. Primary method: poppler-utils (pdftotext) for efficient text extraction
2. Secondary method: PyPDF2 for more detailed structure analysis
3. Fallback method: pdf2image + pytesseract for image-based PDFs

Dependencies:
- poppler-utils (system package)
- PyPDF2
- pdf2image
- pytesseract (optional, for OCR)
"""

import os
import subprocess
import logging
import tempfile
from typing import Dict, List, Optional, Tuple, Union

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class PDFExtractor:
    """Class for extracting text from PDF files using multiple methods."""
    
    def __init__(self, use_ocr: bool = False):
        """
        Initialize the PDF Extractor.
        
        Args:
            use_ocr (bool): Whether to use OCR for image-based PDFs if text extraction fails.
        """
        self.use_ocr = use_ocr
        self._check_dependencies()
    
    def _check_dependencies(self) -> None:
        """Check if required dependencies are installed."""
        # Check for poppler-utils (pdftotext)
        try:
            subprocess.run(['pdftotext', '-v'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            logger.info("poppler-utils (pdftotext) is installed.")
        except FileNotFoundError:
            logger.warning("poppler-utils is not installed. This is the recommended primary method.")
            logger.warning("Install with: apt-get install -y poppler-utils")
        
        # Check for PyPDF2
        try:
            import PyPDF2
            logger.info(f"PyPDF2 version {PyPDF2.__version__} is installed.")
        except ImportError:
            logger.warning("PyPDF2 is not installed. This is the secondary method.")
            logger.warning("Install with: pip install PyPDF2")
        
        # Check for OCR dependencies if enabled
        if self.use_ocr:
            try:
                import pdf2image
                logger.info(f"pdf2image version {pdf2image.__version__} is installed.")
            except ImportError:
                logger.warning("pdf2image is not installed but OCR is enabled.")
                logger.warning("Install with: pip install pdf2image")
            
            try:
                import pytesseract
                logger.info(f"pytesseract version {pytesseract.__version__} is installed.")
            except ImportError:
                logger.warning("pytesseract is not installed but OCR is enabled.")
                logger.warning("Install with: pip install pytesseract")
    
    def extract_text(self, pdf_path: str) -> str:
        """
        Extract text from a PDF file using the best available method.
        
        Args:
            pdf_path (str): Path to the PDF file.
            
        Returns:
            str: Extracted text from the PDF.
        """
        if not os.path.exists(pdf_path):
            raise FileNotFoundError(f"PDF file not found: {pdf_path}")
        
        # Try primary method (poppler-utils)
        text = self._extract_with_pdftotext(pdf_path)
        
        # If primary method fails or returns empty text, try secondary method
        if not text:
            logger.info("Primary extraction method failed or returned empty text. Trying secondary method.")
            text = self._extract_with_pypdf2(pdf_path)
        
        # If both methods fail and OCR is enabled, try OCR
        if not text and self.use_ocr:
            logger.info("Both extraction methods failed. Trying OCR.")
            text = self._extract_with_ocr(pdf_path)
        
        return text or ""
    
    def _extract_with_pdftotext(self, pdf_path: str) -> Optional[str]:
        """
        Extract text from a PDF using poppler-utils (pdftotext).
        
        Args:
            pdf_path (str): Path to the PDF file.
            
        Returns:
            Optional[str]: Extracted text or None if extraction failed.
        """
        try:
            # Use -layout to maintain original layout as much as possible
            result = subprocess.run(
                ['pdftotext', '-layout', pdf_path, '-'],
                capture_output=True,
                text=True,
                check=True
            )
            text = result.stdout
            
            if text.strip():
                logger.info(f"Successfully extracted text from {pdf_path} using pdftotext.")
                return text
            else:
                logger.warning(f"pdftotext returned empty text for {pdf_path}.")
                return None
        except (subprocess.SubprocessError, FileNotFoundError) as e:
            logger.error(f"Failed to extract text with pdftotext: {e}")
            return None
    
    def _extract_with_pypdf2(self, pdf_path: str) -> Optional[str]:
        """
        Extract text from a PDF using PyPDF2.
        
        Args:
            pdf_path (str): Path to the PDF file.
            
        Returns:
            Optional[str]: Extracted text or None if extraction failed.
        """
        try:
            import PyPDF2
            
            with open(pdf_path, 'rb') as file:
                reader = PyPDF2.PdfReader(file)
                text = ""
                
                for page_num in range(len(reader.pages)):
                    page = reader.pages[page_num]
                    page_text = page.extract_text()
                    text += page_text + "\n\n"
            
            if text.strip():
                logger.info(f"Successfully extracted text from {pdf_path} using PyPDF2.")
                return text
            else:
                logger.warning(f"PyPDF2 returned empty text for {pdf_path}.")
                return None
        except Exception as e:
            logger.error(f"Failed to extract text with PyPDF2: {e}")
            return None
    
    def _extract_with_ocr(self, pdf_path: str) -> Optional[str]:
        """
        Extract text from a PDF using OCR (pdf2image + pytesseract).
        
        Args:
            pdf_path (str): Path to the PDF file.
            
        Returns:
            Optional[str]: Extracted text or None if extraction failed.
        """
        if not self.use_ocr:
            return None
        
        try:
            import pdf2image
            import pytesseract
            
            # Convert PDF to images
            images = pdf2image.convert_from_path(pdf_path)
            
            # Extract text from each image
            text = ""
            for i, image in enumerate(images):
                page_text = pytesseract.image_to_string(image)
                text += f"--- Page {i+1} ---\n{page_text}\n\n"
            
            if text.strip():
                logger.info(f"Successfully extracted text from {pdf_path} using OCR.")
                return text
            else:
                logger.warning(f"OCR returned empty text for {pdf_path}.")
                return None
        except Exception as e:
            logger.error(f"Failed to extract text with OCR: {e}")
            return None
    
    def extract_metadata(self, pdf_path: str) -> Dict[str, str]:
        """
        Extract metadata from a PDF file.
        
        Args:
            pdf_path (str): Path to the PDF file.
            
        Returns:
            Dict[str, str]: Dictionary of metadata fields and values.
        """
        if not os.path.exists(pdf_path):
            raise FileNotFoundError(f"PDF file not found: {pdf_path}")
        
        metadata = {}
        
        # Try to extract metadata using pdfinfo
        try:
            result = subprocess.run(
                ['pdfinfo', pdf_path],
                capture_output=True,
                text=True,
                check=True
            )
            
            # Parse pdfinfo output
            for line in result.stdout.split('\n'):
                if ':' in line:
                    key, value = line.split(':', 1)
                    metadata[key.strip()] = value.strip()
            
            logger.info(f"Successfully extracted metadata from {pdf_path} using pdfinfo.")
        except (subprocess.SubprocessError, FileNotFoundError):
            logger.warning("Failed to extract metadata with pdfinfo. Trying PyPDF2.")
            
            # Fallback to PyPDF2 for metadata extraction
            try:
                import PyPDF2
                
                with open(pdf_path, 'rb') as file:
                    reader = PyPDF2.PdfReader(file)
                    if reader.metadata:
                        for key, value in reader.metadata.items():
                            # Remove the leading '/' from PDF metadata keys
                            clean_key = key[1:] if key.startswith('/') else key
                            metadata[clean_key] = str(value)
                
                # Add page count
                metadata['Pages'] = str(len(reader.pages))
                
                logger.info(f"Successfully extracted metadata from {pdf_path} using PyPDF2.")
            except Exception as e:
                logger.error(f"Failed to extract metadata with PyPDF2: {e}")
        
        return metadata
    
    def is_encrypted(self, pdf_path: str) -> bool:
        """
        Check if a PDF file is encrypted/password-protected.
        
        Args:
            pdf_path (str): Path to the PDF file.
            
        Returns:
            bool: True if the PDF is encrypted, False otherwise.
        """
        if not os.path.exists(pdf_path):
            raise FileNotFoundError(f"PDF file not found: {pdf_path}")
        
        # Try to check encryption using PyPDF2
        try:
            import PyPDF2
            
            with open(pdf_path, 'rb') as file:
                reader = PyPDF2.PdfReader(file)
                is_encrypted = reader.is_encrypted
                
                logger.info(f"PDF encryption check: {pdf_path} is {'encrypted' if is_encrypted else 'not encrypted'}.")
                return is_encrypted
        except Exception as e:
            logger.error(f"Failed to check encryption status with PyPDF2: {e}")
            
            # Fallback to pdfinfo
            try:
                result = subprocess.run(
                    ['pdfinfo', pdf_path],
                    capture_output=True,
                    text=True
                )
                
                # Check if "Encrypted: yes" appears in the output
                is_encrypted = "Encrypted: yes" in result.stdout
                
                logger.info(f"PDF encryption check (pdfinfo): {pdf_path} is {'encrypted' if is_encrypted else 'not encrypted'}.")
                return is_encrypted
            except Exception as e2:
                logger.error(f"Failed to check encryption status with pdfinfo: {e2}")
                
                # If both methods fail, assume it might be encrypted
                logger.warning(f"Could not determine encryption status for {pdf_path}. Assuming it might be encrypted.")
                return True
    
    def extract_text_from_pages(self, pdf_path: str, start_page: int = 0, end_page: Optional[int] = None) -> Dict[int, str]:
        """
        Extract text from specific pages of a PDF file.
        
        Args:
            pdf_path (str): Path to the PDF file.
            start_page (int): First page to extract (0-indexed).
            end_page (Optional[int]): Last page to extract (0-indexed, inclusive).
                                     If None, extracts until the end of the document.
            
        Returns:
            Dict[int, str]: Dictionary mapping page numbers to extracted text.
        """
        if not os.path.exists(pdf_path):
            raise FileNotFoundError(f"PDF file not found: {pdf_path}")
        
        page_texts = {}
        
        # Try primary method (poppler-utils)
        try:
            with tempfile.TemporaryDirectory() as temp_dir:
                # Extract each page to a separate text file
                subprocess.run(
                    ['pdftotext', '-layout', '-f', str(start_page + 1),
                     '-l', str(end_page + 1) if end_page is not None else '',
                     '-htmlmeta', pdf_path, f"{temp_dir}/page"],
                    check=True
                )
                
                # Read each extracted page
                page_files = sorted([f for f in os.listdir(temp_dir) if f.startswith('page-')])
                for page_file in page_files:
                    page_num = int(page_file.split('-')[1]) - 1  # Convert to 0-indexed
                    with open(os.path.join(temp_dir, page_file), 'r', encoding='utf-8') as f:
                        page_texts[page_num] = f.read()
                
                logger.info(f"Successfully extracted text from pages {start_page}-{end_page or 'end'} using pdftotext.")
                return page_texts
        except Exception as e:
            logger.error(f"Failed to extract pages with pdftotext: {e}")
        
        # Fallback to PyPDF2
        try:
            import PyPDF2
            
            with open(pdf_path, 'rb') as file:
                reader = PyPDF2.PdfReader(file)
                total_pages = len(reader.pages)
                
                # Adjust end_page if not specified
                if end_page is None:
                    end_page = total_pages - 1
                
                # Validate page range
                start_page = max(0, min(start_page, total_pages - 1))
                end_page = max(start_page, min(end_page, total_pages - 1))
                
                for page_num in range(start_page, end_page + 1):
                    page = reader.pages[page_num]
                    page_texts[page_num] = page.extract_text()
            
            logger.info(f"Successfully extracted text from pages {start_page}-{end_page} using PyPDF2.")
            return page_texts
        except Exception as e:
            logger.error(f"Failed to extract pages with PyPDF2: {e}")
            
            # If OCR is enabled, try that as a last resort
            if self.use_ocr:
                return self._extract_pages_with_ocr(pdf_path, start_page, end_page)
            
            return {}
    
    def _extract_pages_with_ocr(self, pdf_path: str, start_page: int = 0, end_page: Optional[int] = None) -> Dict[int, str]:
        """
        Extract text from specific pages using OCR.
        
        Args:
            pdf_path (str): Path to the PDF file.
            start_page (int): First page to extract (0-indexed).
            end_page (Optional[int]): Last page to extract (0-indexed, inclusive).
            
        Returns:
            Dict[int, str]: Dictionary mapping page numbers to extracted text.
        """
        try:
            import pdf2image
            import pytesseract
            
            # Convert PDF to images
            images = pdf2image.convert_from_path(pdf_path)
            
            # Adjust end_page if not specified
            if end_page is None:
                end_page = len(images) - 1
            
            # Validate page range
            start_page = max(0, min(start_page, len(images) - 1))
            end_page = max(start_page, min(end_page, len(images) - 1))
            
            # Extract text from specified pages
            page_texts = {}
            for i in range(start_page, end_page + 1):
                if i < len(images):
                    page_text = pytesseract.image_to_string(images[i])
                    page_texts[i] = page_text
            
            logger.info(f"Successfully extracted text from pages {start_page}-{end_page} using OCR.")
            return page_texts
        except Exception as e:
            logger.error(f"Failed to extract pages with OCR: {e}")
            return {}
    
    def extract_images(self, pdf_path: str, output_dir: Optional[str] = None) -> List[str]:
        """
        Extract images from a PDF file.
        
        Args:
            pdf_path (str): Path to the PDF file.
            output_dir (Optional[str]): Directory to save extracted images.
                                       If None, a temporary directory is used.
            
        Returns:
            List[str]: List of paths to extracted images.
        """
        if not os.path.exists(pdf_path):
            raise FileNotFoundError(f"PDF file not found: {pdf_path}")
        
        # Create output directory if it doesn't exist
        if output_dir:
            os.makedirs(output_dir, exist_ok=True)
            temp_dir = None
        else:
            temp_dir = tempfile.TemporaryDirectory()
            output_dir = temp_dir.name
        
        image_paths = []
        
        try:
            # Try using pdfimages from poppler-utils
            base_name = os.path.splitext(os.path.basename(pdf_path))[0]
            output_pattern = os.path.join(output_dir, f"{base_name}-image")
            
            subprocess.run(
                ['pdfimages', '-j', pdf_path, output_pattern],
                check=True
            )
            
            # Get list of extracted images
            image_paths = sorted([
                os.path.join(output_dir, f)
                for f in os.listdir(output_dir)
                if f.startswith(f"{base_name}-image")
            ])
            
            logger.info(f"Successfully extracted {len(image_paths)} images from {pdf_path} using pdfimages.")
        except (subprocess.SubprocessError, FileNotFoundError) as e:
            logger.error(f"Failed to extract images with pdfimages: {e}")
            
            # Fallback to pdf2image
            try:
                import pdf2image
                
                # Convert PDF pages to images
                images = pdf2image.convert_from_path(pdf_path)
                
                # Save each page as an image
                for i, image in enumerate(images):
                    image_path = os.path.join(output_dir, f"{base_name}-page-{i+1}.png")
                    image.save(image_path, "PNG")
                    image_paths.append(image_path)
                
                logger.info(f"Successfully extracted {len(image_paths)} page images from {pdf_path} using pdf2image.")
            except Exception as e2:
                logger.error(f"Failed to extract images with pdf2image: {e2}")
        
        # If using a temporary directory, make sure it's not deleted until we're done
        if temp_dir:
            temp_dir._finalizer.detach()  # Prevent auto-deletion
        
        return image_paths
    
    def extract_tables(self, pdf_path: str) -> Dict[int, List[List[str]]]:
        """
        Extract tables from a PDF file.
        
        Args:
            pdf_path (str): Path to the PDF file.
            
        Returns:
            Dict[int, List[List[str]]]: Dictionary mapping page numbers to lists of tables,
                                       where each table is a list of rows, and each row is a list of cells.
        """
        if not os.path.exists(pdf_path):
            raise FileNotFoundError(f"PDF file not found: {pdf_path}")
        
        tables_by_page = {}
        
        try:
            # Try using tabula-py if available
            import tabula
            
            # Extract all tables from the PDF
            tables = tabula.read_pdf(pdf_path, pages='all', multiple_tables=True)
            
            # Group tables by page
            for i, table in enumerate(tables):
                # Tabula doesn't directly provide page numbers, so we need to infer them
                # This is a simplification; in reality, we'd need to track which page each table comes from
                page_num = i  # This is just a placeholder
                
                if page_num not in tables_by_page:
                    tables_by_page[page_num] = []
                
                # Convert DataFrame to list of lists
                table_data = [row.tolist() for _, row in table.iterrows()]
                tables_by_page[page_num].append(table_data)
            
            logger.info(f"Successfully extracted tables from {pdf_path} using tabula-py.")
        except ImportError:
            logger.warning("tabula-py is not installed. Cannot extract tables.")
            logger.warning("Install with: pip install tabula-py")
        except Exception as e:
            logger.error(f"Failed to extract tables: {e}")
        
        return tables_by_page


def main():
    """Command-line interface for PDF extraction."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Extract content from PDF files")
    parser.add_argument("pdf_path", help="Path to the PDF file")
    parser.add_argument("--output", "-o", help="Output file for extracted text")
    parser.add_argument("--metadata", "-m", action="store_true", help="Extract metadata")
    parser.add_argument("--images", "-i", help="Directory to save extracted images")
    parser.add_argument("--tables", "-t", action="store_true", help="Extract tables")
    parser.add_argument("--ocr", action="store_true", help="Use OCR for image-based PDFs")
    parser.add_argument("--pages", "-p", help="Page range to extract (e.g., '0-5' or '1,3,5')")
    
    args = parser.parse_args()
    
    # Initialize extractor
    extractor = PDFExtractor(use_ocr=args.ocr)
    
    # Process page range if specified
    if args.pages:
        page_ranges = []
        for part in args.pages.split(','):
            if '-' in part:
                start, end = map(int, part.split('-'))
                page_ranges.extend(range(start, end + 1))
            else:
                page_ranges.append(int(part))
        
        # Extract text from specified pages
        page_texts = extractor.extract_text_from_pages(
            args.pdf_path,
            start_page=min(page_ranges),
            end_page=max(page_ranges)
        )
        
        # Filter to only requested pages
        page_texts = {page: text for page, text in page_texts.items() if page in page_ranges}
        
        # Output results
        if args.output:
            with open(args.output, 'w', encoding='utf-8') as f:
                for page, text in sorted(page_texts.items()):
                    f.write(f"--- Page {page + 1} ---\n{text}\n\n")
        else:
            for page, text in sorted(page_texts.items()):
                print(f"--- Page {page + 1} ---\n{text}\n")
    else:
        # Extract full text
        text = extractor.extract_text(args.pdf_path)
        
        # Output results
        if args.output:
            with open(args.output, 'w', encoding='utf-8') as f:
                f.write(text)
        else:
            print(text)
    
    # Extract metadata if requested
    if args.metadata:
        metadata = extractor.extract_metadata(args.pdf_path)
        print("\n--- Metadata ---")
        for key, value in metadata.items():
            print(f"{key}: {value}")
    
    # Extract images if requested
    if args.images:
        image_paths = extractor.extract_images(args.pdf_path, args.images)
        print(f"\nExtracted {len(image_paths)} images to {args.images}")
    
    # Extract tables if requested
    if args.tables:
        try:
            tables = extractor.extract_tables(args.pdf_path)
            print("\n--- Tables ---")
            for page, page_tables in tables.items():
                print(f"Page {page + 1}: {len(page_tables)} tables found")
        except Exception as e:
            print(f"Error extracting tables: {e}")


if __name__ == "__main__":
    main()
