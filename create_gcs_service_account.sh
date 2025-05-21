#!/bin/bash

# Skript för att skapa ett tjänstekonto för Google Cloud Storage
# och generera en JSON-nyckel för autentisering

GCLOUD_CMD="/Users/hanneszachari/google-cloud-sdk/bin/gcloud"
SERVICE_ACCOUNT_NAME="storage-access"
SERVICE_ACCOUNT_DISPLAY_NAME="Storage Access Service Account"
KEY_FILE_PATH="$HOME/storage-access-key.json"

# Kontrollera om gcloud är installerat
if [ ! -f "$GCLOUD_CMD" ]; then
    echo "Fel: gcloud CLI hittades inte på $GCLOUD_CMD"
    echo "Kontrollera att Google Cloud SDK är installerat."
    exit 1
fi

# Kontrollera om användaren är inloggad
echo "Kontrollerar Google Cloud-autentisering..."
if ! $GCLOUD_CMD auth print-access-token &> /dev/null; then
    echo "Du är inte inloggad i Google Cloud. Loggar in..."
    $GCLOUD_CMD auth login
    
    if [ $? -ne 0 ]; then
        echo "Fel: Kunde inte logga in i Google Cloud."
        exit 1
    fi
fi

# Hämta projekt-ID
PROJECT_ID=$($GCLOUD_CMD config get-value project 2>/dev/null)
if [ -z "$PROJECT_ID" ]; then
    echo "Inget projekt-ID är konfigurerat. Hämtar tillgängliga projekt..."
    PROJECTS=$($GCLOUD_CMD projects list --format="value(projectId)" 2>/dev/null)
    
    if [ -z "$PROJECTS" ]; then
        echo "Inga projekt hittades. Ange ett projekt-ID manuellt:"
        read -p "Projekt-ID: " PROJECT_ID
    else
        echo "Tillgängliga projekt:"
        echo "$PROJECTS" | nl
        echo "Välj ett projekt genom att ange numret:"
        read -p "Val: " PROJECT_NUM
        PROJECT_ID=$(echo "$PROJECTS" | sed -n "${PROJECT_NUM}p")
    fi
    
    if [ -z "$PROJECT_ID" ]; then
        echo "Inget projekt-ID angavs. Använder 'hannesjz' som standard."
        PROJECT_ID="hannesjz"
    fi
    
    echo "Sätter projekt-ID till: $PROJECT_ID"
    $GCLOUD_CMD config set project "$PROJECT_ID"
else
    echo "Använder projekt-ID: $PROJECT_ID"
fi

# Skapa tjänstekonto om det inte redan finns
echo "Kontrollerar om tjänstekontot $SERVICE_ACCOUNT_NAME redan finns..."
if ! $GCLOUD_CMD iam service-accounts describe "$SERVICE_ACCOUNT_NAME@$PROJECT_ID.iam.gserviceaccount.com" &> /dev/null; then
    echo "Skapar tjänstekonto $SERVICE_ACCOUNT_NAME..."
    $GCLOUD_CMD iam service-accounts create "$SERVICE_ACCOUNT_NAME" \
        --display-name="$SERVICE_ACCOUNT_DISPLAY_NAME"
    
    if [ $? -ne 0 ]; then
        echo "Fel: Kunde inte skapa tjänstekontot."
        exit 1
    fi
    
    echo "Tjänstekontot har skapats."
else
    echo "Tjänstekontot $SERVICE_ACCOUNT_NAME finns redan."
fi

# Tilldela behörigheter till tjänstekontot
echo "Tilldelar behörigheter till tjänstekontot..."
$GCLOUD_CMD projects add-iam-policy-binding "$PROJECT_ID" \
    --member="serviceAccount:$SERVICE_ACCOUNT_NAME@$PROJECT_ID.iam.gserviceaccount.com" \
    --role="roles/storage.objectAdmin"

if [ $? -ne 0 ]; then
    echo "Varning: Kunde inte tilldela behörigheter till tjänstekontot."
    echo "Du kan behöva göra detta manuellt i Google Cloud Console."
else
    echo "Behörigheter har tilldelats."
fi

# Skapa JSON-nyckel
echo "Skapar JSON-nyckel för tjänstekontot..."
$GCLOUD_CMD iam service-accounts keys create "$KEY_FILE_PATH" \
    --iam-account="$SERVICE_ACCOUNT_NAME@$PROJECT_ID.iam.gserviceaccount.com"

if [ $? -ne 0 ]; then
    echo "Fel: Kunde inte skapa JSON-nyckeln."
    exit 1
fi

echo "JSON-nyckeln har skapats och sparats till: $KEY_FILE_PATH"
echo ""
echo "Du kan nu använda denna nyckel för att autentisera mot Google Cloud Storage."
echo "För att använda nyckeln med gsutil, kör:"
echo "export GOOGLE_APPLICATION_CREDENTIALS=\"$KEY_FILE_PATH\""
echo ""
echo "För att använda med RunPod, ange följande information:"
echo "- Service Account JSON: $KEY_FILE_PATH"
echo "- Bucket Path: $PROJECT_ID/Fakturor_och_Kvitton"
echo "- Pod Path: /workspace/data"