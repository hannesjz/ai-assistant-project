# Dokumentprocessor för Fakturor och Kvitton

Detta verktyg hjälper dig att bearbeta PDF-dokument som har laddats upp till Google Cloud Storage, extrahera text och metadata, och möjliggör sökning i dokumenten.

## Funktioner

- **Förbättrad PDF-extrahering med OCR**: Extraherar text från PDF-filer och använder OCR när det behövs
- **Metadata-extrahering**: Identifierar automatiskt fakturanummer, datum, belopp, moms, företagsnamn och organisationsnummer
- **Avancerad sökfunktion**: Stöd för både exakt sökning och fuzzy-sökning i dokumenten
- **Google Cloud Storage-integration**: Laddar ner, bearbetar och laddar upp filer direkt från/till din GCS-bucket

## Installation

1. Installera nödvändiga systempaket:

### För macOS:
Använd det medföljande installationsskriptet:

```bash
./install_macos_dependencies.sh
```

Detta skript kommer att:
- Installera Homebrew om det inte redan finns
- Installera poppler (för pdftotext)
- Installera tesseract med språkpaket
- Installera Python-beroenden

### För Ubuntu/Debian:

```bash
sudo apt-get update
sudo apt-get install -y poppler-utils tesseract-ocr tesseract-ocr-swe
pip install -r requirements.txt
```

3. Konfigurera Google Cloud-autentisering och projekt:

Skriptet `process_documents.sh` kommer automatiskt att:
- Konfigurera Google Cloud-autentisering om det behövs
- Hämta och sätta rätt projekt-ID
- Kontrollera om bucketen finns

Men du kan också göra det manuellt:

```bash
# Autentisera med ditt Google-konto
/Users/hanneszachari/google-cloud-sdk/bin/gcloud auth application-default login

# Sätt projekt-ID
/Users/hanneszachari/google-cloud-sdk/bin/gcloud config set project "hannesjz"

# Eller genom att ange sökväg till tjänstekontofil
export GOOGLE_APPLICATION_CREDENTIALS="/path/to/service-account-key.json"
export GOOGLE_CLOUD_PROJECT="hannesjz"
```

## Användning

### Grundläggande användning

```bash
python document_processor.py --bucket hannesjz-files
```

Detta kommer att:
1. Ladda ner alla filer från din GCS-bucket
2. Bearbeta alla PDF-filer (extrahera text och metadata)
3. Spara resultaten lokalt

### Avancerad användning

```bash
python document_processor.py \
  --bucket hannesjz-files \
  --prefix "Fakturor/" \
  --local-dir "./downloaded_docs" \
  --output-dir "./processed_docs" \
  --upload \
  --upload-prefix "processed_documents"
```

Detta kommer att:
1. Ladda ner filer från "Fakturor/"-katalogen i din GCS-bucket
2. Spara dem i "./downloaded_docs"
3. Bearbeta PDF-filerna och spara resultaten i "./processed_docs"
4. Ladda upp de bearbetade filerna till "processed_documents/"-katalogen i din GCS-bucket

### Sökning i dokument

```bash
python document_processor.py \
  --bucket hannesjz-files \
  --output-dir "./processed_docs" \
  --search "elgiganten" \
  --fuzzy
```

Detta kommer att:
1. Söka efter "elgiganten" i de bearbetade dokumenten
2. Använda fuzzy-sökning för att hitta liknande träffar
3. Visa sökresultaten

## Exempel på arbetsflöde

1. Ladda upp dokument till Google Cloud Storage (redan gjort)
2. Bearbeta dokumenten och extrahera text/metadata:

```bash
python document_processor.py --bucket hannesjz-files --upload
```

3. Sök efter specifika fakturor:

```bash
python document_processor.py --bucket hannesjz-files --output-dir "./processed_docs" --search "elgiganten"
```

4. Analysera resultaten lokalt eller i Google Cloud Storage

## Tips

- För stora dokumentsamlingar, använd `--prefix` för att bearbeta en delmängd av filerna
- Använd `--fuzzy` för att hitta dokument även när sökfrågan inte exakt matchar texten
- Metadata sparas i JSON-format för enkel integrering med andra system