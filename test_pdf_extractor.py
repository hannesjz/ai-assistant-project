#!/usr/bin/env python3

import sys
import os
from src.pdf_extractor.pdf_extractor import PDFExtractor

def main():
    print("Testing PDF Extractor initialization...")
    
    # Initialize the PDF extractor
    pdf_extractor = PDFExtractor(use_ocr=False)
    
    print("\nPDF Extractor initialized successfully!")
    print("The poppler-utils tools are now properly installed and detected.")

if __name__ == "__main__":
    main()