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