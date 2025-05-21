# Systemarkitektur för Ekonomisk Rådgivare

## Översikt

Ekonomisk Rådgivare är ett omfattande system för bearbetning, analys och visualisering av finansiella dokument. Systemet är utformat för att hantera olika typer av finansiella dokument (fakturor, kvitton, budgetar, etc.), extrahera relevant information från dem, och sedan presentera denna information genom olika visualiseringar och analyser för att underlätta ekonomisk beslutsfattande.

## Systemarkitektur

Systemet är uppbyggt med en modulär arkitektur som består av flera huvudkomponenter:

### 1. Dokumentbearbetning
- **PDF Extractor**: Extraherar text och data från PDF-dokument
- **Excel/CSV Extractor**: Läser och bearbetar data från Excel och CSV-filer
- **OCR-integration**: Använder optisk teckenigenkänning för att extrahera text från skannade dokument

### 2. Indexering och Metadata
- **Document Indexer**: Indexerar dokument och extraherar metadata
- **Metadata Storage**: Lagrar metadata i JSON-format för enkel åtkomst

### 3. Datavisualisering
- **Data Visualizer**: Skapar statiska och interaktiva visualiseringar av finansiell data
- **Dashboard Generator**: Genererar omfattande dashboards med flera visualiseringar

### 4. Semantisk Sökning
- **Semantic Search**: Möjliggör sökning baserad på betydelse snarare än exakta nyckelord
- **Document Clustering**: Grupperar liknande dokument automatiskt
- **Entity Recognition**: Extraherar entiteter som företag, personer, belopp och datum

### 5. Användargränssnitt
- **Command-Line Interface**: Tillhandahåller kommandoradsverktyg för att interagera med systemet
- **Script-baserade verktyg**: Förenklar vanliga operationer genom skript

## Komponentbeskrivning

### PDF Extractor (src/pdf_extractor/)

#### Klasser:
- **PDFExtractor**: Grundläggande klass för att extrahera text från PDF-dokument
- **EnhancedPDFExtractor**: Utökad version med OCR-stöd för skannade dokument

#### Funktionalitet:
- Extraherar text från PDF-dokument
- Använder PyPDF2 för att läsa PDF-filer
- Integrerar med Tesseract OCR för att extrahera text från bilder
- Konverterar PDF-sidor till bilder med pdf2image
- Extraherar metadata som dokumenttyp, leverantör, belopp och datum

#### Arbetsflöde:
1. Öppna PDF-fil
2. För varje sida:
   - Försök extrahera text direkt
   - Om texten är otillräcklig, konvertera sidan till bild och använd OCR
3. Analysera extraherad text för att identifiera metadata
4. Returnera extraherad text och metadata

### Excel/CSV Extractor (src/excel_csv_extractor/)

#### Klasser:
- **ExcelCsvExtractor**: Klass för att läsa och bearbeta data från Excel och CSV-filer

#### Funktionalitet:
- Läser data från Excel och CSV-filer
- Konverterar data till strukturerat format
- Extraherar metadata från tabelldata

#### Arbetsflöde:
1. Identifiera filtyp (Excel eller CSV)
2. Läs data med lämplig metod (pandas för båda formaten)
3. Bearbeta data för att extrahera relevant information
4. Returnera strukturerad data och metadata

### Document Indexer (src/indexing/)

#### Klasser:
- **DocumentIndexer**: Klass för att indexera dokument och extrahera metadata

#### Funktionalitet:
- Analyserar dokument för att identifiera dokumenttyp
- Extraherar metadata som leverantör, belopp, datum, etc.
- Skapar sökbart index av dokument
- Lagrar metadata i JSON-format

#### Arbetsflöde:
1. Ta emot dokument (text eller strukturerad data)
2. Analysera innehåll för att identifiera dokumenttyp
3. Extrahera metadata baserat på dokumenttyp
4. Skapa index och lagra metadata
5. Spara metadata till JSON-fil

### Data Visualizer (src/data_visualization/)

#### Klasser:
- **DataVisualizer**: Klass för att skapa visualiseringar baserade på metadata

#### Funktionalitet:
- Skapar statiska visualiseringar med matplotlib och seaborn
- Skapar interaktiva visualiseringar med plotly
- Stödjer olika typer av visualiseringar:
  - Tidsserieanalys
  - Leverantörsfördelning
  - Dokumenttypsfördelning
  - Säsongsvariationer
  - Beloppsfördelning
- Genererar dashboards med flera visualiseringar
- Exporterar datasammanfattningar

#### Arbetsflöde:
1. Läs metadata från JSON-fil
2. Konvertera metadata till pandas DataFrame
3. Bearbeta data för visualisering
4. Skapa visualiseringar baserat på användarens val
5. Spara visualiseringar till filer (PNG för statiska, HTML för interaktiva)

### Semantic Search (src/semantic_search/)

#### Klasser:
- **SemanticSearch**: Klass för semantisk sökning och analys av dokument

#### Funktionalitet:
- Möjliggör sökning baserad på betydelse snarare än exakta nyckelord
- Stödjer fuzzy matching för att hantera stavfel
- Grupperar liknande dokument med K-means clustering
- Extraherar entiteter som företag, personer, belopp och datum
- Analyserar trender i metadata
- Identifierar relaterade termer baserat på samförekomst

#### Arbetsflöde:
1. Läs dokument och metadata
2. Förbehandla text (tokenisering, stoppordsborttagning, stemming)
3. Skapa dokumentvektorer med TF-IDF
4. Utför clustering med K-means
5. Extrahera entiteter med regex eller spaCy
6. Besvara sökfrågor genom att beräkna likhet mellan fråga och dokument
7. Analysera trender och mönster i metadata

## Dataflöde

Det övergripande dataflödet i systemet är:

1. **Inmatning**: Dokument (PDF, Excel, CSV) placeras i en inmatningskatalog
2. **Bearbetning**: 
   - PDF-dokument bearbetas av PDFExtractor/EnhancedPDFExtractor
   - Excel/CSV-filer bearbetas av ExcelCsvExtractor
3. **Indexering**: 
   - Extraherad data indexeras av DocumentIndexer
   - Metadata skapas och lagras i JSON-format
4. **Sökning och Analys**:
   - SemanticSearch läser dokument och metadata
   - Användaren kan söka efter dokument och analysera data
5. **Visualisering**:
   - DataVisualizer läser metadata
   - Skapar visualiseringar baserat på användarens val
6. **Output**:
   - Visualiseringar sparas som PNG- eller HTML-filer
   - Datasammanfattningar exporteras som textfiler

## Teknologier och Bibliotek

### Huvudbibliotek
- **pandas**: Datamanipulering och analys
- **numpy**: Numeriska beräkningar
- **matplotlib**: Statiska visualiseringar
- **seaborn**: Avancerade statistiska visualiseringar
- **plotly**: Interaktiva visualiseringar
- **PyPDF2**: PDF-bearbetning
- **pytesseract**: OCR (Optical Character Recognition)
- **pdf2image**: Konvertering av PDF till bilder för OCR
- **Pillow**: Bildbearbetning
- **nltk**: Naturlig språkbearbetning
- **scikit-learn**: Maskininlärning (för clustering och vektorisering)
- **spacy**: Avancerad NLP och entitetsigenkänning

### Andra verktyg och teknologier
- **Google Cloud Storage**: För lagring av dokument (baserat på importerade moduler)
- **difflib**: För textjämförelser
- **argparse**: För kommandoradsargument
- **logging**: För loggning
- **json**: För hantering av JSON-data
- **pathlib**: För plattformsoberoende filsökvägshantering

## Designmönster

Systemet använder flera designmönster för att uppnå modularitet, flexibilitet och underhållbarhet:

### 1. Factory Pattern
- Används för att skapa lämpliga extractors baserat på filtyp
- Exempel: Välja mellan PDFExtractor och EnhancedPDFExtractor baserat på om OCR behövs

### 2. Strategy Pattern
- Används för olika visualiseringsstrategier
- Exempel: Olika metoder för att visualisera data (tidsserie, fördelning, etc.)

### 3. Repository Pattern
- Används för dataåtkomst och lagring
- Exempel: Metadata lagras i JSON-format och åtkomst sker genom abstrakta metoder

### 4. Facade Pattern
- Används för att förenkla komplexa undersystem
- Exempel: DataVisualizer tillhandahåller ett enkelt gränssnitt för att skapa olika typer av visualiseringar

### 5. Command Pattern
- Används i kommandoradsgränssnittet
- Exempel: run_semantic.sh skript som översätter kommandoradsargument till operationer

## API-integrationer

Systemet har följande API-integrationer:

### 1. Tesseract OCR
- Integration med Tesseract OCR-motor via pytesseract
- Används för att extrahera text från bilder och skannade dokument

### 2. Google Cloud Storage (potentiell)
- Integration med Google Cloud Storage för dokumentlagring
- Baserat på importerade moduler, men implementationsdetaljer är inte fullständigt dokumenterade

### 3. spaCy NLP
- Integration med spaCy för avancerad naturlig språkbearbetning
- Används för entitetsigenkänning i dokument

## Filstruktur

```
my-project-name/
├── src/
│   ├── excel_csv_extractor/
│   │   ├── __init__.py
│   │   └── excel_csv_extractor.py
│   ├── indexing/
│   │   ├── __init__.py
│   │   └── document_indexer.py
│   ├── pdf_extractor/
│   │   ├── __init__.py
│   │   ├── pdf_extractor.py
│   │   └── enhanced_pdf_extractor.py
│   ├── data_visualization/
│   │   ├── __init__.py
│   │   └── data_visualizer.py
│   ├── semantic_search/
│   │   ├── __init__.py
│   │   └── semantic_search.py
│   ├── examples/
│   │   ├── data_visualizer_example.py
│   │   └── semantic_visualization_example.py
│   ├── tests/
│   │   ├── __init__.py
│   │   ├── test_enhanced_pdf_extractor.py
│   │   ├── test_file_integration.py
│   │   └── test_data_visualizer.py
│   ├── utils/
│   │   ├── __init__.py
│   │   └── file_utils.py
│   ├── main.py
│   ├── main_enhanced.py
│   └── main_semantic.py
├── data/
├── processed_docs/
├── test_files/
├── visualizations/
├── requirements.txt
├── setup.sh
├── setup_and_run.sh
├── process_documents.sh
├── run_semantic.sh
├── README.md
├── README_DOCUMENT_PROCESSOR.md
├── README_SEMANTIC_SEARCH.md
└── INSTALLATION.md
```

## Utvecklingsstatus

Systemet har nått en betydande utvecklingsnivå med flera funktionella komponenter:

### Implementerade funktioner:
1. **Dokumentbearbetning**: PDF, Excel och CSV-bearbetning med OCR-stöd
2. **Indexering**: Dokumentindexering och metadataextrahering
3. **Datavisualisering**: Statiska och interaktiva visualiseringar
4. **Semantisk sökning**: Avancerad sökning, clustering och entitetsigenkänning

### Pågående utveckling:
1. **Användargränssnitt**: Förbättring av användargränssnitt för enklare interaktion
2. **Integration**: Förbättrad integration mellan komponenter
3. **Testning**: Utökad testning av alla komponenter

### Framtida utvecklingsmöjligheter:
1. **Webbaserat gränssnitt**: Utveckling av ett webbaserat användargränssnitt
2. **Maskininlärning**: Implementering av mer avancerade ML-tekniker för dokumentklassificering
3. **API-integration**: Integration med ekonomisystem och andra externa tjänster
4. **Skalbarhet**: Förbättringar för att hantera större datamängder

## Användningsfall

Systemet stödjer följande huvudsakliga användningsfall:

### 1. Dokumentbearbetning
- Extrahera text och data från PDF-dokument, inklusive skannade dokument
- Läsa och bearbeta data från Excel och CSV-filer
- Extrahera metadata som dokumenttyp, leverantör, belopp och datum

### 2. Dokumentsökning
- Söka efter dokument baserat på nyckelord
- Använda semantisk sökning för att hitta relevanta dokument
- Filtrera sökresultat baserat på metadata

### 3. Dataanalys
- Analysera trender i finansiell data
- Identifiera mönster i utgifter
- Gruppera liknande dokument
- Extrahera entiteter från dokument

### 4. Datavisualisering
- Skapa tidsserieanalyser av finansiella mätvärden
- Visualisera leverantörsfördelning och utgiftsmönster
- Visa dokumenttypsfördelning
- Analysera säsongsvariationer i utgifter
- Skapa interaktiva visualiseringar för djupare analys

## Slutsats

Ekonomisk Rådgivare är ett omfattande system för bearbetning, analys och visualisering av finansiella dokument. Systemet kombinerar flera avancerade tekniker inom dokumentbearbetning, naturlig språkbearbetning, dataanalys och visualisering för att ge användare värdefulla insikter i finansiell data.

Systemets modulära arkitektur möjliggör enkel utbyggnad och underhåll, medan användningen av moderna bibliotek och tekniker säkerställer effektiv och robust funktionalitet. Med fortsatt utveckling har systemet potential att bli ett kraftfullt verktyg för ekonomisk analys och beslutsfattande.