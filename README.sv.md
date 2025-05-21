# AI-assistent med Google Cloud Storage och GitHub-integration

## Projektöversikt

Detta projekt implementerar en avancerad AI-assistent som integrerar med Google Cloud Storage och GitHub för att bearbeta, analysera och underhålla minne av dokument. Systemet utnyttjar RunPod's högpresterande beräkningsresurser och Hugging Face-modeller för förbättrad dokumentbearbetning.

## Huvudfunktioner

1. **Google Cloud Storage-integration**
   - Automatisk synkronisering med din GCS bucket (hannesjz-files)
   - Filhämtning, uppladdning och övervakning av ändringar
   - Robust felhantering och återhämtning

2. **GitHub-integration**
   - Automatiska commits och push till ditt repository
   - Generering av beskrivande commit-meddelanden
   - Säker konfiguration med dina GitHub-uppgifter

3. **Dokumentbearbetning**
   - Stöd för PDF, Excel, CSV och textfiler
   - OCR och metadataextrahering
   - Semantisk analys och vektorrepresentation

4. **Minneshantering**
   - Persistent lagring av dokument och metadata
   - Vektorbaserad sökning och hämtning
   - Relationsspårning mellan dokument

5. **Hugging Face-modellintegration**
   - Dokumentembedding för semantisk sökning
   - Named Entity Recognition (NER)
   - Automatisk sammanfattning

## Systemarkitektur

Systemet är uppbyggt av följande huvudkomponenter:

```
+------------------------------------------+
|                                          |
|           RunPod Environment             |
|  (2x RTX 3090, 32 vCPU, 115GB RAM)       |
|                                          |
+------------------------------------------+
                    |
        +-----------+-----------+
        |                       |
+-------v-------+      +--------v--------+
|               |      |                 |
| Google Cloud  |      |    GitHub       |
| Storage       |      |    Repository   |
| Integration   |      |    Integration  |
|               |      |                 |
+-------+-------+      +--------+--------+
        |                       |
        |      +--------+      |
        +----->|        |<-----+
               |  Core  |
        +----->|  AI    |<-----+
        |      |        |      |
        |      +----+---+      |
        |           |          |
+-------v-------+   |   +------v---------+
|               |   |   |                |
| Document      |   |   | Memory         |
| Processing    |   |   | Management     |
| Pipeline      |   |   | System         |
|               |   |   |                |
+-------+-------+   |   +--------+-------+
        |           |            |
        |      +----v---+        |
        +----->|        |<-------+
               | Hugging|
               | Face   |
               | Models |
               |        |
               +--------+
```

1. **GCS-klient** - Hanterar all interaktion med Google Cloud Storage
2. **GitHub-klient** - Hanterar versionshantering och automatiska commits
3. **Minneshanteringssystem** - Lagrar och hanterar dokumentinformation
4. **Hugging Face-modeller** - Tillhandahåller AI-funktioner för dokumentanalys
5. **Huvudapplikation** - Koordinerar alla komponenter och hanterar arbetsflödet

## Installation och konfiguration

### Förutsättningar

- Python 3.10 eller senare
- RunPod-miljö med 2x RTX 3090, 32 vCPU, 115GB RAM
- Docker-container: runpod/pytorch:2.1.0-py3.10-cuda11.8.0-devel-ubuntu22.04

### Installation

1. Klona GitHub-repositoryt:
   ```bash
   git clone https://github.com/hannesjz/my-project-name.git
   cd my-project-name
   ```

2. Installera beroenden:
   ```bash
   pip install -r requirements.txt
   ```

3. Konfigurera systemet genom att redigera `config.json`:
   ```json
   {
     "gcs": {
       "bucket_name": "hannesjz-files",
       "credentials_path": "/path/to/credentials.json",
       "local_cache_dir": "./gcs_cache"
     },
     "github": {
       "repo_url": "https://github.com/hannesjz/my-project-name.git",
       "local_path": "./github_repo",
       "username": "hannesjz",
       "email": "hannes_zachari@hotmail.com",
       "auto_commit_interval_minutes": 30
     },
     "memory": {
       "db_path": "./memory/memory.db",
       "vector_dimension": 768,
       "max_documents": 10000
     },
     "huggingface": {
       "cache_dir": "./models",
       "device": null,
       "multi_gpu": true
     }
   }
   ```

## Användning

### Starta AI-assistenten

```bash
python src/ai_assistant/main.py
```

Detta startar assistenten som kommer att:
1. Ansluta till din Google Cloud Storage bucket
2. Övervaka ändringar i bucket
3. Bearbeta nya dokument automatiskt
4. Lagra information i minneshanteringssystemet
5. Commita ändringar till GitHub med jämna mellanrum

### Söka efter dokument

```bash
python src/ai_assistant/main.py --search "din sökfråga här"
```

### Visa systemstatus

```bash
python src/ai_assistant/main.py --stats
```

## Projektstruktur

```
ai_assistant/
├── src/
│   ├── ai_assistant/
│   │   ├── gcs_integration/
│   │   │   ├── __init__.py
│   │   │   └── gcs_client.py
│   │   ├── github_integration/
│   │   │   ├── __init__.py
│   │   │   └── github_client.py
│   │   ├── memory_management/
│   │   │   ├── __init__.py
│   │   │   └── memory_system.py
│   │   ├── huggingface_integration/
│   │   │   ├── __init__.py
│   │   │   └── model_client.py
│   │   ├── core/
│   │   │   ├── __init__.py
│   │   │   └── ai_assistant.py
│   │   ├── __init__.py
│   │   └── main.py
│   └── utils/
│       └── __init__.py
├── requirements.txt
├── setup.sh
└── config.json
```

## Tekniska detaljer

### Google Cloud Storage-integration

GCS-klienten hanterar all interaktion med din bucket, inklusive:
- Autentisering med säkra credentials
- Fillistning och filtrering
- Asynkron nedladdning och uppladdning
- Övervakning av ändringar med callback-funktion
- Metadatahantering för filer

### GitHub-integration

GitHub-klienten hanterar versionshantering och automatiska commits:
- Konfiguration med dina GitHub-uppgifter
- Automatisk staging av ändrade filer
- Generering av beskrivande commit-meddelanden
- Periodisk push till main-branch
- Felhantering och återförsök

### Minneshanteringssystem

Minneshanteringssystemet lagrar och hanterar all dokumentinformation:
- SQLite-databas för persistent lagring
- Lagring av dokumentinnehåll, metadata och vektorer
- Vektorbaserad sökning med cosine similarity
- Relationsspårning mellan relaterade dokument
- Pruning-funktionalitet för att hantera stora datamängder

### Hugging Face-modellintegration

Hugging Face-modellerna tillhandahåller avancerade AI-funktioner:
- Dokumentembedding med sentence-transformers
- Named Entity Recognition för att extrahera viktig information
- Automatisk sammanfattning av långa dokument
- Optimerad inferens på GPU med stöd för multi-GPU
- Modellcaching för förbättrad prestanda

## Prestandaoptimering

Systemet är optimerat för att utnyttja RunPod's högpresterande resurser:
- Multi-GPU-stöd för parallell inferens
- Batchbearbetning av dokument
- Asynkron filhämtning och uppladdning
- Effektiv minneshantering för stora datamängder
- Caching av modeller och resultat

## Felsökning

### Vanliga problem

1. **Anslutningsproblem med GCS**
   - Kontrollera att credentials-filen är korrekt och har rätt behörigheter
   - Verifiera att bucket-namnet är korrekt

2. **GitHub-autentiseringsfel**
   - Kontrollera att användarnamn och e-post är korrekt konfigurerade
   - Säkerställ att repository-URL:en är korrekt

3. **GPU-relaterade problem**
   - Kontrollera att CUDA är korrekt installerat
   - Verifiera att PyTorch är kompilerat med CUDA-stöd

### Loggning

Systemet använder omfattande loggning för att underlätta felsökning:
- Huvudloggfil: ai_assistant.log

## Kontakt och support

För frågor eller support, kontakta:
- E-post: hannes_zachari@hotmail.com
- GitHub: https://github.com/hannesjz