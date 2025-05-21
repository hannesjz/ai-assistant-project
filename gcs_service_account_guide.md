# Kopiera från Google Cloud Storage med Service Account

Denna guide visar hur du skapar ett tjänstekonto (Service Account) för Google Cloud Storage och använder det för att kopiera filer till en pod.

## 1. Skapa ett Service Account i Google Cloud

1. Gå till [Google Cloud Console](https://console.cloud.google.com/)
2. Välj ditt projekt "hannesjz"
3. Gå till "IAM & Admin" > "Service Accounts"
4. Klicka på "Create Service Account"
5. Ange ett namn, t.ex. "storage-access"
6. Klicka på "Create and Continue"
7. Tilldela rollen "Storage Object Viewer" för läsåtkomst (eller "Storage Object Admin" för skriv/läs)
8. Klicka på "Continue" och sedan "Done"

## 2. Skapa en JSON-nyckel för Service Account

1. I listan över tjänstekonton, klicka på det nyligen skapade kontot
2. Gå till fliken "Keys"
3. Klicka på "Add Key" > "Create new key"
4. Välj "JSON" som nyckeltyp
5. Klicka på "Create"
6. En JSON-fil kommer att laddas ner till din dator - spara denna på en säker plats

## 3. Använd Service Account JSON för att kopiera filer

### Alternativ 1: Använda gsutil med Service Account

```bash
# Sätt miljövariabel för autentisering
export GOOGLE_APPLICATION_CREDENTIALS="/sökväg/till/din/service-account-key.json"

# Kopiera filer från GCS till lokal mapp
gsutil -m cp -r gs://hannesjz-files/Fakturor_och_Kvitton/* /lokal/målmapp/
```

### Alternativ 2: Kopiera till en Kubernetes Pod

1. Skapa en Kubernetes Secret från Service Account JSON:

```bash
kubectl create secret generic gcs-key --from-file=key.json=/sökväg/till/din/service-account-key.json
```

2. Montera Secret i din Pod och använd det för att kopiera filer:

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: gcs-copy-pod
spec:
  containers:
  - name: gcs-copy-container
    image: google/cloud-sdk:slim
    command:
    - "/bin/bash"
    - "-c"
    - |
      export GOOGLE_APPLICATION_CREDENTIALS=/var/secrets/google/key.json
      gsutil -m cp -r gs://hannesjz-files/Fakturor_och_Kvitton/* /mnt/data/
    volumeMounts:
    - name: gcs-key
      mountPath: /var/secrets/google
      readOnly: true
    - name: data
      mountPath: /mnt/data
  volumes:
  - name: gcs-key
    secret:
      secretName: gcs-key
  - name: data
    emptyDir: {}
```

### Alternativ 3: Använda med RunPod

För att använda med RunPod, behöver du:

1. Service Account JSON-fil
2. Bucket-sökväg: `hannesjz-files/Fakturor_och_Kvitton`
3. Pod-sökväg: `/workspace/data`

Konfigurera i RunPod-gränssnittet:
- Under "Storage" > "Add Storage"
- Välj "Google Cloud Storage"
- Ladda upp din Service Account JSON-fil
- Ange Bucket Path: `hannesjz-files/Fakturor_och_Kvitton`
- Ange Pod Path: `/workspace/data`

## 4. Skapa Service Account JSON med gcloud CLI

Du kan också skapa ett tjänstekonto och generera JSON-nyckeln direkt från kommandoraden:

```bash
# Skapa ett nytt tjänstekonto
/Users/hanneszachari/google-cloud-sdk/bin/gcloud iam service-accounts create storage-access \
  --display-name="Storage Access Service Account"

# Tilldela behörigheter
/Users/hanneszachari/google-cloud-sdk/bin/gcloud projects add-iam-policy-binding hannesjz \
  --member="serviceAccount:storage-access@hannesjz.iam.gserviceaccount.com" \
  --role="roles/storage.objectAdmin"

# Skapa och ladda ner JSON-nyckeln
/Users/hanneszachari/google-cloud-sdk/bin/gcloud iam service-accounts keys create ~/storage-access-key.json \
  --iam-account=storage-access@hannesjz.iam.gserviceaccount.com
```

Ersätt `hannesjz` med ditt faktiska projekt-ID och justera e-postadressen för tjänstekontot enligt ditt projekt.