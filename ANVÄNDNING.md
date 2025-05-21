# Användarguide för Ekonomisk Rådgivare

Denna guide beskriver hur du använder filintegrationsmodulen för din personliga ekonomiska rådgivare.

## Komma igång

Efter att ha installerat systemet enligt instruktionerna i [INSTALLATION.md](INSTALLATION.md), kan du börja använda filintegrationsmodulen.

## Grundläggande användning

### Indexera filer

För att indexera filer i en katalog, använd följande kommando:

```bash
python src/main.py --index /sökväg/till/dina/dokument
```

Detta kommer att:
1. Söka igenom katalogen efter PDF-, Excel- och CSV-filer
2. Extrahera text och data från filerna
3. Indexera innehållet för snabb sökning
4. Visa statistik om indexeringsprocessen

För att begränsa indexeringen till specifika filtyper eller ändra andra inställningar, skapa en anpassad konfigurationsfil (se avsnittet om konfiguration nedan).

### Söka efter dokument

För att söka efter dokument i indexet, använd följande kommando:

```bash
python src/main.py --search "sökfras"
```

Du kan begränsa antalet sökresultat med `--limit`-parametern:

```bash
python src/main.py --search "faktura 2023" --limit 5
```

Sökresultaten visas i JSON-format med följande information:
- Dokumentets ID
- Filsökväg
- Filtyp
- Relevans (sökpoäng)
- Metadata (t.ex. datum, författare, etc.)
- Utdrag från innehållet med sökfrasen markerad

### Visa statistik

För att visa statistik om indexet, kör programmet utan parametrar:

```bash
python src/main.py
```

Detta visar information om:
- Antal indexerade dokument per filtyp
- Total storlek på indexet
- Senaste indexeringstidpunkt
- Vanliga söktermer

## Avancerad användning

### Anpassad konfiguration

Du kan anpassa systemets beteende genom att skapa en konfigurationsfil i JSON-format:

```json
{
  "data_dir": "./min_data",
  "index_type": "whoosh",
  "use_ocr": true,
  "max_files_per_batch": 50,
  "supported_file_types": [".pdf", ".xlsx", ".xls", ".csv", ".txt"]
}
```

Använd konfigurationsfilen med `--config`-parametern:

```bash
python src/main.py --config min_konfiguration.json --index /sökväg/till/dina/dokument
```

### Strukturerad sökning

För mer avancerade sökningar kan du använda API:et direkt i dina egna Python-skript:

```python
from src.main import EkonomiskRadgivare

# Initiera rådgivaren
advisor = EkonomiskRadgivare("config.json")

# Sök med filter
results = advisor.search("faktura", 
                        filters={"file_type": "pdf", "date": "2023-01-01:2023-12-31"}, 
                        limit=10)

# Strukturerad sökning
results = advisor.search_structured({
    "amount": ">1000",
    "recipient": "Företag AB",
    "date": "2023-01-01:2023-12-31"
})

# Hämta ett specifikt dokument
document = advisor.get_document("doc_id_12345")
```

## Filtyper och funktioner

### PDF-filer

Systemet kan extrahera text från PDF-filer på flera sätt:
- Direkt textextrahering för sökbara PDF-filer
- Poppler-baserad extrahering för mer komplexa PDF-filer
- OCR (optisk teckenigenkänning) för inskannade dokument (om aktiverat)

Metadata som extraheras inkluderar:
- Författare
- Skapandedatum
- Titel
- Nyckelord
- Antal sidor

### Excel-filer

För Excel-filer extraheras:
- Data från alla kalkylblad
- Kalkylbladsnamn
- Formler (om tillgängliga)
- Metadata (författare, skapandedatum, etc.)

### CSV-filer

För CSV-filer:
- Automatisk detektering av avgränsare (komma, semikolon, tab, etc.)
- Automatisk kodningsdetektering
- Kolumntypsigenkänning

## Felsökning och tips

### Optimera indexering

För stora datamängder:
1. Öka `max_files_per_batch` för snabbare indexering
2. Använd `sqlite` som indextyp för bättre prestanda
3. Inaktivera OCR om det inte behövs

### Förbättra sökresultat

För bättre sökresultat:
1. Använd specifika söktermer
2. Kombinera flera söktermer för att begränsa resultaten
3. Använd citattecken för exakta fraser: `"exakt fras"`

### Vanliga problem

- **Långsam indexering**: Kontrollera att OCR är inaktiverat om det inte behövs
- **Saknade sökresultat**: Kontrollera att filerna har indexerats korrekt
- **Minnesproblem**: Minska `max_files_per_batch` för att använda mindre minne

## Kommandoreferens

| Kommando | Beskrivning | Exempel |
|----------|-------------|---------|
| `--index` | Indexera filer i en katalog | `python src/main.py --index ./dokument` |
| `--search` | Sök efter dokument | `python src/main.py --search "faktura"` |
| `--config` | Använd en anpassad konfigurationsfil | `python src/main.py --config min_config.json` |
| `--limit` | Begränsa antalet sökresultat | `python src/main.py --search "kvitto" --limit 5` |
