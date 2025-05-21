# Installationsguide för Ekonomisk Rådgivare

Denna guide beskriver hur du installerar och konfigurerar filintegrationsmodulen för din personliga ekonomiska rådgivare.

## Systemkrav

- Python 3.10 eller senare
- Minst 4 GB RAM (8 GB rekommenderas för större datamängder)
- Minst 1 GB ledigt diskutrymme
- Operativsystem: macOS, Linux eller Windows

## Installation

### Steg 1: Installera Python-beroenden

Installera först de nödvändiga Python-paketen:

```bash
# Grundläggande beroenden
pip install pandas openpyxl PyPDF2 nltk

# För OCR-funktionalitet (valfritt)
pip install pdf2image pytesseract
```

### Steg 2: Installera systempaket

#### För Linux (Ubuntu/Debian):

```bash
# För PDF-hantering
sudo apt-get install poppler-utils

# För OCR-funktionalitet (valfritt)
sudo apt-get install tesseract-ocr tesseract-ocr-swe
```

#### För macOS:

```bash
# Installera Homebrew om det inte redan är installerat
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# För PDF-hantering
brew install poppler

# För OCR-funktionalitet (valfritt)
brew install tesseract tesseract-lang
```

#### För Windows:

1. Ladda ner och installera [Poppler för Windows](https://github.com/oschwartz10612/poppler-windows/releases/)
2. Lägg till Poppler-katalogen till din PATH-miljövariabel
3. För OCR-funktionalitet (valfritt), ladda ner och installera [Tesseract för Windows](https://github.com/UB-Mannheim/tesseract/wiki)

### Steg 3: Ladda ner och installera projektet

1. Klona projektet från GitHub:

```bash
git clone https://github.com/din-användare/ekonomisk-radgivare.git
cd ekonomisk-radgivare
```

2. Installera projektet:

```bash
pip install -e .
```

### Steg 4: Konfigurera systemet

Skapa en konfigurationsfil `config.json` i projektets rotkatalog:

```json
{
  "data_dir": "./data",
  "index_type": "sqlite",
  "use_ocr": false,
  "max_files_per_batch": 100,
  "supported_file_types": [".pdf", ".xlsx", ".xls", ".csv"]
}
```

Anpassa inställningarna efter dina behov:

- `data_dir`: Katalog där indexerade data lagras
- `index_type`: Typ av index att använda ("sqlite" eller "whoosh")
- `use_ocr`: Aktivera OCR för PDF-filer som inte innehåller sökbar text
- `max_files_per_batch`: Maximalt antal filer att bearbeta i en batch
- `supported_file_types`: Lista över filtyper som ska stödjas

### Steg 5: Skapa datakatalog

Skapa datakatalogen där indexerade data kommer att lagras:

```bash
mkdir -p data
```

## Verifiera installationen

För att verifiera att installationen fungerar korrekt, kör integrationstestet:

```bash
python src/tests/test_file_integration.py ./exempel_data --output ./test_results
```

Om testet körs utan fel och genererar testresultat i `./test_results`-katalogen, är installationen klar.

## Felsökning

### Problem med PDF-extrahering

Om du stöter på problem med PDF-extrahering, kontrollera att:

1. Poppler är korrekt installerat och finns i din PATH
2. PDF-filerna inte är lösenordsskyddade eller krypterade
3. För OCR-funktionalitet, kontrollera att Tesseract är korrekt installerat

### Problem med Excel/CSV-extrahering

Om du stöter på problem med Excel/CSV-extrahering, kontrollera att:

1. pandas och openpyxl är korrekt installerade
2. Excel-filerna inte är lösenordsskyddade
3. CSV-filerna använder en standardkodning (UTF-8, ISO-8859-1, etc.)

### Problem med indexering

Om du stöter på problem med indexering, kontrollera att:

1. Du har skrivrättigheter till datakatalogen
2. SQLite är korrekt installerat (ingår vanligtvis i Python)
3. För Whoosh-indexering, kontrollera att Whoosh-paketet är installerat (`pip install whoosh`)
