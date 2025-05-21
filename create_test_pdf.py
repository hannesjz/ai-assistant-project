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