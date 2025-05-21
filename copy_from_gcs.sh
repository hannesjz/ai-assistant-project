#!/bin/bash

# Skript för att kopiera filer från Google Cloud Storage med hjälp av ett tjänstekonto
# Användning: ./copy_from_gcs.sh [service-account-key.json] [bucket-name] [source-path] [destination-path]

# Standardvärden
SERVICE_ACCOUNT_KEY="$HOME/storage-access-key.json"
BUCKET_NAME="hannesjz-files"
SOURCE_PATH="Fakturor_och_Kvitton"
DESTINATION_PATH="./downloaded_data"
GSUTIL_CMD="/Users/hanneszachari/google-cloud-sdk/bin/gsutil"

# Kontrollera om argument har angetts
if [ -n "$1" ]; then
    SERVICE_ACCOUNT_KEY="$1"
fi

if [ -n "$2" ]; then
    BUCKET_NAME="$2"
fi

if [ -n "$3" ]; then
    SOURCE_PATH="$3"
fi

if [ -n "$4" ]; then
    DESTINATION_PATH="$4"
fi

# Kontrollera om gsutil är installerat
if [ ! -f "$GSUTIL_CMD" ]; then
    echo "Fel: gsutil CLI hittades inte på $GSUTIL_CMD"
    echo "Kontrollera att Google Cloud SDK är installerat."
    exit 1
fi

# Kontrollera om tjänstekontonyckeln finns
if [ ! -f "$SERVICE_ACCOUNT_KEY" ]; then
    echo "Fel: Tjänstekontonyckeln hittades inte på $SERVICE_ACCOUNT_KEY"
    echo "Skapa en tjänstekontofil med ./create_gcs_service_account.sh först."
    exit 1
fi

# Skapa destinationskatalogen om den inte finns
mkdir -p "$DESTINATION_PATH"

# Sätt miljövariabel för autentisering
export GOOGLE_APPLICATION_CREDENTIALS="$SERVICE_ACCOUNT_KEY"

echo "Kopierar filer från gs://$BUCKET_NAME/$SOURCE_PATH till $DESTINATION_PATH..."

# Kopiera filer med gsutil
$GSUTIL_CMD -m cp -r "gs://$BUCKET_NAME/$SOURCE_PATH/*" "$DESTINATION_PATH/"

if [ $? -ne 0 ]; then
    echo "Fel: Kunde inte kopiera filerna."
    echo "Kontrollera att tjänstekontot har rätt behörigheter och att bucket-sökvägen är korrekt."
    exit 1
fi

echo "Filerna har kopierats framgångsrikt till $DESTINATION_PATH"
echo ""
echo "För att använda med RunPod, ange följande information:"
echo "- Service Account JSON: $SERVICE_ACCOUNT_KEY"
echo "- Bucket Path: $BUCKET_NAME/$SOURCE_PATH"
echo "- Pod Path: /workspace/data"