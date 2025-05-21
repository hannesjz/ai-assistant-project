# RunPod Google Cloud Storage Konfiguration

## Copy from Google Cloud Storage

### Service Account JSON
Ladda upp filen `hannesjz-c8e146f2e36e.json` som innehåller ditt service account.

### Location
#### Bucket Path: 
```
hannesjz-files/Fakturor_och_Kvitton
```

Där:
- `hannesjz-files` är namnet på din bucket
- `Fakturor_och_Kvitton` är mappen i din bucket

### Copy to Pod
#### Pod Path:
```
/workspace/data
```

Detta är sökvägen i din pod där filerna kommer att kopieras till.

## Steg-för-steg instruktioner för RunPod

1. Gå till RunPod-gränssnittet
2. Välj din pod eller skapa en ny
3. Under "Storage" eller "Volumes", klicka på "Add Storage"
4. Välj "Google Cloud Storage"
5. Under "Service Account JSON", ladda upp filen `hannesjz-c8e146f2e36e.json`
6. Under "Bucket Path", ange `hannesjz-files/Fakturor_och_Kvitton`
7. Under "Pod Path", ange `/workspace/data`
8. Klicka på "Add" eller "Save"

När din pod startar kommer filerna från Google Cloud Storage automatiskt att kopieras till `/workspace/data` i din pod.