# Google Cloud Storage Scripts

Dessa skript hjälper dig att skapa ett tjänstekonto för Google Cloud Storage och kopiera filer från din bucket till en lokal mapp eller en pod.

## Innehåll

1. **create_gcs_service_account.sh** - Skapar ett tjänstekonto och genererar en JSON-nyckel
2. **copy_from_gcs.sh** - Kopierar filer från Google Cloud Storage med hjälp av tjänstekontot
3. **gcs_service_account_guide.md** - Detaljerad guide för att skapa och använda tjänstekonton

## Snabbstart

### 1. Skapa ett tjänstekonto och JSON-nyckel

```bash
./create_gcs_service_account.sh
```

Detta skript kommer att:
- Kontrollera om du är inloggad i Google Cloud
- Hämta och sätta rätt projekt-ID
- Skapa ett tjänstekonto med namnet "storage-access"
- Tilldela behörigheter för att läsa/skriva till Google Cloud Storage
- Generera en JSON-nyckel och spara den i din hemkatalog

### 2. Kopiera filer från Google Cloud Storage

```bash
./copy_from_gcs.sh
```

Detta skript kommer att:
- Använda JSON-nyckeln för att autentisera mot Google Cloud Storage
- Kopiera filer från din bucket till en lokal mapp
- Visa information om hur du kan använda samma konfiguration med RunPod

Du kan också ange egna parametrar:

```bash
./copy_from_gcs.sh [service-account-key.json] [bucket-name] [source-path] [destination-path]
```

Exempel:
```bash
./copy_from_gcs.sh ~/storage-access-key.json hannesjz-files Fakturor_och_Kvitton ./downloaded_data
```

## Användning med RunPod

För att använda med RunPod, behöver du:

1. Service Account JSON-fil (skapas med `create_gcs_service_account.sh`)
2. Bucket-sökväg: `hannesjz-files/Fakturor_och_Kvitton`
3. Pod-sökväg: `/workspace/data`

Konfigurera i RunPod-gränssnittet:
- Under "Storage" > "Add Storage"
- Välj "Google Cloud Storage"
- Ladda upp din Service Account JSON-fil
- Ange Bucket Path: `hannesjz-files/Fakturor_och_Kvitton`
- Ange Pod Path: `/workspace/data`

## Mer information

Se `gcs_service_account_guide.md` för en detaljerad guide om hur du skapar och använder tjänstekonton för Google Cloud Storage.