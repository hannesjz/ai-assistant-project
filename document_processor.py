#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Document Processor för Fakturor och Kvitton
-------------------------------------------
Detta skript implementerar förbättrad PDF-extrahering med OCR,
metadata-extrahering och avancerad sökfunktionalitet för dokument
som lagras i Google Cloud Storage.
"""

import os
import re
import logging
import tempfile
import subprocess
import argparse
from difflib import SequenceMatcher
from pathlib import Path
from google.cloud import storage
from PIL import Image
import pytesseract
from pdf2image import convert_from_path

# Konfigurera loggning
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def extract_text_from_pdf(pdf_path, use_ocr=True):
    """Extrahera text från PDF-fil med pdftotext och OCR vid behov."""
    logger.info(f"Extraherar text från: {pdf_path}")
    
    # Försök först med pdftotext
    with tempfile.NamedTemporaryFile(suffix='.txt') as temp:
        try:
            subprocess.run(['pdftotext', pdf_path, temp.name], check=True)
            
            # Läs extraherad text
            with open(temp.name, 'r') as f:
                text = f.read()
            
            # Om texten är för kort, prova med OCR
            if len(text.strip()) < 100 and use_ocr:
                logger.info(f"Lite text extraherad, provar med OCR: {pdf_path}")
                
                # Konvertera PDF till bilder
                images = convert_from_path(pdf_path)
                
                # Extrahera text från varje bild med OCR
                ocr_text = []
                for i, image in enumerate(images):
                    text = pytesseract.image_to_string(image, lang='swe+eng')
                    ocr_text.append(text)
                
                text = "\n".join(ocr_text)
            
            return text
        except subprocess.CalledProcessError:
            logger.error(f"Kunde inte extrahera text från {pdf_path}")
            return ""
        except Exception as e:
            logger.error(f"Fel vid textextrahering: {e}")
            return ""

def extract_metadata_from_text(text):
    """Extrahera metadata från text."""
    metadata = {}
    
    # Extrahera fakturanummer
    invoice_number_match = re.search(r'faktura\s*nr\.?\s*:?\s*(\d+)', text, re.IGNORECASE)
    if invoice_number_match:
        metadata['invoice_number'] = invoice_number_match.group(1)
    
    # Extrahera datum
    date_match = re.search(r'datum\s*:?\s*(\d{4}-\d{2}-\d{2}|\d{2}-\d{2}-\d{4}|\d{2}/\d{2}/\d{4})', text, re.IGNORECASE)
    if date_match:
        metadata['date'] = date_match.group(1)
    
    # Extrahera belopp
    amount_match = re.search(r'belopp\s*:?\s*(\d+[\s\.,]\d+)\s*(?:kr|SEK)', text, re.IGNORECASE)
    if amount_match:
        metadata['amount'] = amount_match.group(1).replace(' ', '').replace(',', '.')
    
    # Extrahera moms
    vat_match = re.search(r'moms\s*:?\s*(\d+[\s\.,]\d+)\s*(?:kr|SEK)', text, re.IGNORECASE)
    if vat_match:
        metadata['vat'] = vat_match.group(1).replace(' ', '').replace(',', '.')
    
    # Extrahera avsändare/företag
    company_patterns = [
        r'(?:från|avsändare|företag):\s*([A-Za-zåäöÅÄÖ0-9\s]+)',
        r'^([A-Za-zåäöÅÄÖ0-9\s]+)(?:AB|HB|KB)',
        r'([A-Za-zåäöÅÄÖ0-9\s]+)(?:AB|HB|KB)'
    ]
    
    for pattern in company_patterns:
        company_match = re.search(pattern, text, re.IGNORECASE | re.MULTILINE)
        if company_match:
            metadata['company'] = company_match.group(1).strip()
            break
    
    # Extrahera organisationsnummer
    org_number_match = re.search(r'org(?:anisations)?(?:\.|\s)?n(?:umme)?r(?:\.|\s)?:?\s*(\d{6}-?\d{4}|\d{10})', text, re.IGNORECASE)
    if org_number_match:
        metadata['org_number'] = org_number_match.group(1)
    
    return metadata

def search_documents(query, data_dir, fuzzy=True, metadata_filter=None):
    """Sök i dokument med stöd för fuzzy-sökning och metadata-filtrering."""
    # Läs extraherade textfiler
    text_files = [os.path.join(data_dir, f) for f in os.listdir(data_dir) if f.endswith('.txt')]
    
    # Sök i textfilerna
    matches = []
    for text_file in text_files:
        try:
            with open(text_file, 'r') as f:
                content = f.read().lower()
            
            # Kontrollera metadata-filter om det finns
            if metadata_filter:
                metadata_file = text_file.replace('.txt', '.metadata.json')
                if os.path.exists(metadata_file):
                    import json
                    with open(metadata_file, 'r') as f:
                        metadata = json.load(f)
                    
                    # Kontrollera om metadata matchar filtret
                    match_metadata = True
                    for key, value in metadata_filter.items():
                        if key not in metadata or metadata[key] != value:
                            match_metadata = False
                            break
                    
                    if not match_metadata:
                        continue
            
            # Exakt sökning
            if query.lower() in content:
                matches.append((text_file, 1.0))  # Perfekt matchning
            # Fuzzy-sökning
            elif fuzzy:
                # Dela upp innehållet i ord
                words = content.split()
                
                # Beräkna bästa matchning för varje ord
                best_match = 0
                for word in words:
                    similarity = SequenceMatcher(None, query.lower(), word).ratio()
                    if similarity > best_match:
                        best_match = similarity
                
                # Om matchningen är tillräckligt bra, lägg till i resultatet
                if best_match > 0.8:
                    matches.append((text_file, best_match))
        except Exception as e:
            logger.error(f"Fel vid sökning i {text_file}: {e}")
    
    # Sortera efter matchningskvalitet
    matches.sort(key=lambda x: x[1], reverse=True)
    
    return [m[0] for m in matches]

def download_from_gcs(bucket_name, prefix, local_dir):
    """Ladda ner filer från Google Cloud Storage."""
    logger.info(f"Laddar ner filer från gs://{bucket_name}/{prefix} till {local_dir}")
    
    # Skapa lokal katalog om den inte finns
    os.makedirs(local_dir, exist_ok=True)
    
    # Hämta projekt-ID från miljövariabel
    project_id = os.environ.get('GOOGLE_CLOUD_PROJECT')
    
    # Initiera GCS-klient
    if project_id:
        logger.info(f"Använder projekt-ID: {project_id}")
        storage_client = storage.Client(project=project_id)
    else:
        logger.warning("Inget projekt-ID angivet. Försöker använda standardvärden.")
        storage_client = storage.Client()
    
    bucket = storage_client.bucket(bucket_name)
    
    # Lista alla objekt med angivet prefix
    blobs = bucket.list_blobs(prefix=prefix)
    
    # Ladda ner varje objekt
    for blob in blobs:
        # Skapa lokal filsökväg
        relative_path = blob.name[len(prefix):].lstrip('/')
        local_path = os.path.join(local_dir, relative_path)
        
        # Skapa katalogstruktur om den inte finns
        os.makedirs(os.path.dirname(local_path), exist_ok=True)
        
        # Ladda ner filen
        logger.info(f"Laddar ner: {blob.name} -> {local_path}")
        blob.download_to_filename(local_path)
    
    logger.info("Nedladdning klar")

def process_documents(local_dir, output_dir):
    """Bearbeta alla PDF-dokument i den lokala katalogen."""
    logger.info(f"Bearbetar dokument i {local_dir}")
    
    # Skapa utdatakatalog om den inte finns
    os.makedirs(output_dir, exist_ok=True)
    
    # Hitta alla PDF-filer
    pdf_files = []
    for root, _, files in os.walk(local_dir):
        for file in files:
            if file.lower().endswith('.pdf'):
                pdf_files.append(os.path.join(root, file))
    
    logger.info(f"Hittade {len(pdf_files)} PDF-filer")
    
    # Bearbeta varje PDF-fil
    for pdf_file in pdf_files:
        try:
            # Extrahera text
            text = extract_text_from_pdf(pdf_file)
            
            # Extrahera metadata
            metadata = extract_metadata_from_text(text)
            
            # Skapa filnamn för utdata
            base_name = os.path.basename(pdf_file)
            text_file = os.path.join(output_dir, f"{os.path.splitext(base_name)[0]}.txt")
            metadata_file = os.path.join(output_dir, f"{os.path.splitext(base_name)[0]}.metadata.json")
            
            # Spara text
            with open(text_file, 'w') as f:
                f.write(text)
            
            # Spara metadata
            import json
            with open(metadata_file, 'w') as f:
                json.dump(metadata, f, ensure_ascii=False, indent=2)
            
            logger.info(f"Bearbetade: {pdf_file}")
        except Exception as e:
            logger.error(f"Fel vid bearbetning av {pdf_file}: {e}")

def upload_to_gcs(local_dir, bucket_name, prefix):
    """Ladda upp bearbetade filer till Google Cloud Storage."""
    logger.info(f"Laddar upp filer från {local_dir} till gs://{bucket_name}/{prefix}")
    
    # Hämta projekt-ID från miljövariabel
    project_id = os.environ.get('GOOGLE_CLOUD_PROJECT')
    
    # Initiera GCS-klient
    if project_id:
        logger.info(f"Använder projekt-ID: {project_id}")
        storage_client = storage.Client(project=project_id)
    else:
        logger.warning("Inget projekt-ID angivet. Försöker använda standardvärden.")
        storage_client = storage.Client()
    
    bucket = storage_client.bucket(bucket_name)
    
    # Hitta alla filer att ladda upp
    for root, _, files in os.walk(local_dir):
        for file in files:
            local_path = os.path.join(root, file)
            
            # Skapa GCS-sökväg
            relative_path = os.path.relpath(local_path, local_dir)
            gcs_path = os.path.join(prefix, relative_path)
            
            # Ladda upp filen
            blob = bucket.blob(gcs_path)
            logger.info(f"Laddar upp: {local_path} -> {gcs_path}")
            blob.upload_from_filename(local_path)
    
    logger.info("Uppladdning klar")

def main():
    """Huvudfunktion för dokumentbearbetning."""
    parser = argparse.ArgumentParser(description='Bearbeta dokument från Google Cloud Storage')
    parser.add_argument('--bucket', required=True, help='GCS bucket-namn')
    parser.add_argument('--prefix', default='', help='Prefix för filer i GCS')
    parser.add_argument('--local-dir', default='./documents', help='Lokal katalog för nedladdade filer')
    parser.add_argument('--output-dir', default='./processed', help='Katalog för bearbetade filer')
    parser.add_argument('--upload', action='store_true', help='Ladda upp bearbetade filer till GCS')
    parser.add_argument('--upload-prefix', default='processed', help='Prefix för uppladdade filer i GCS')
    parser.add_argument('--search', help='Sökfråga för att söka i bearbetade dokument')
    parser.add_argument('--fuzzy', action='store_true', help='Använd fuzzy-sökning')
    
    args = parser.parse_args()
    
    # Skapa kataloger
    os.makedirs(args.local_dir, exist_ok=True)
    os.makedirs(args.output_dir, exist_ok=True)
    
    # Ladda ner filer från GCS
    download_from_gcs(args.bucket, args.prefix, args.local_dir)
    
    # Bearbeta dokument
    process_documents(args.local_dir, args.output_dir)
    
    # Sök i dokument om en sökfråga angavs
    if args.search:
        results = search_documents(args.search, args.output_dir, fuzzy=args.fuzzy)
        print(f"Sökresultat för '{args.search}':")
        for result in results:
            print(f"- {result}")
    
    # Ladda upp bearbetade filer till GCS om det begärdes
    if args.upload:
        upload_to_gcs(args.output_dir, args.bucket, args.upload_prefix)

if __name__ == '__main__':
    main()