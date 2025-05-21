#!/bin/bash

# Skript för att köra dokumentprocessorn med vanliga inställningar
# Användning: ./process_documents.sh [sökfråga]

# Konfigurera variabler
BUCKET_NAME="hannesjz-files"
LOCAL_DIR="./downloaded_docs"
OUTPUT_DIR="./processed_docs"
UPLOAD_PREFIX="processed_documents"
GCLOUD_CMD="/Users/hanneszachari/google-cloud-sdk/bin/gcloud"
GSUTIL_CMD="/Users/hanneszachari/google-cloud-sdk/bin/gsutil"

# Hitta Python-kommandot
PYTHON_CMD=""
if command -v python3 &> /dev/null; then
    PYTHON_CMD="python3"
elif command -v python &> /dev/null; then
    PYTHON_CMD="python"
else
    echo "Fel: Kunde inte hitta Python. Installera Python 3 och försök igen."
    echo "Du kan installera Python från https://www.python.org/downloads/"
    exit 1
fi

echo "Använder Python-kommando: $PYTHON_CMD"

# Skapa kataloger om de inte finns
mkdir -p "$LOCAL_DIR"
mkdir -p "$OUTPUT_DIR"

# Kontrollera om Google Cloud-autentisering är konfigurerad
echo "Kontrollerar Google Cloud-autentisering..."
if ! $GCLOUD_CMD auth application-default print-access-token &> /dev/null; then
    echo "Google Cloud-autentisering saknas. Konfigurerar..."
    $GCLOUD_CMD auth application-default login
    
    if [ $? -ne 0 ]; then
        echo "Fel: Kunde inte konfigurera Google Cloud-autentisering."
        echo "Du kan konfigurera det manuellt med kommandot:"
        echo "  $GCLOUD_CMD auth application-default login"
        exit 1
    fi
fi

echo "Google Cloud-autentisering är konfigurerad."

# Hämta och sätt projekt-ID
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

# Exportera projekt-ID som miljövariabel för Google Cloud-klienten
export GOOGLE_CLOUD_PROJECT="$PROJECT_ID"

# Kontrollera om bucketen finns
echo "Kontrollerar om bucketen $BUCKET_NAME finns..."
if ! $GSUTIL_CMD ls gs://$BUCKET_NAME &> /dev/null; then
    echo "Varning: Bucketen $BUCKET_NAME hittades inte eller så har du inte åtkomst till den."
    echo "Kontrollera att bucketen finns och att du har rätt behörigheter."
    
    # Fråga användaren om de vill fortsätta
    read -p "Vill du fortsätta ändå? (j/n): " CONTINUE
    if [[ ! "$CONTINUE" =~ ^[jJ]$ ]]; then
        echo "Avbryter."
        exit 1
    fi
fi

# Kontrollera om en sökfråga angavs
if [ -n "$1" ]; then
    echo "Söker efter: $1"
    $PYTHON_CMD document_processor.py \
        --bucket "$BUCKET_NAME" \
        --local-dir "$LOCAL_DIR" \
        --output-dir "$OUTPUT_DIR" \
        --search "$1" \
        --fuzzy
else
    echo "Bearbetar dokument från $BUCKET_NAME"
    $PYTHON_CMD document_processor.py \
        --bucket "$BUCKET_NAME" \
        --local-dir "$LOCAL_DIR" \
        --output-dir "$OUTPUT_DIR" \
        --upload \
        --upload-prefix "$UPLOAD_PREFIX"
fi

echo "Klart!"