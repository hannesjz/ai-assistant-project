# Setting Up GitHub Access on RunPod for Ekonomisk Rådgivare

This guide will help you set up GitHub access on your RunPod instance to clone and work with the Ekonomisk Rådgivare repository.

## GitHub Authentication

GitHub no longer supports password authentication for Git operations. Instead, you need to use one of these methods:

1. Personal Access Token (PAT)
2. SSH Key Authentication

## Method 1: Using a Personal Access Token (Recommended)

### Step 1: Generate a Personal Access Token on GitHub

1. Go to GitHub and log in to your account
2. Click on your profile picture in the top-right corner
3. Select "Settings"
4. Scroll down and click on "Developer settings" in the left sidebar
5. Click on "Personal access tokens" → "Tokens (classic)"
6. Click "Generate new token" → "Generate new token (classic)"
7. Give your token a descriptive name (e.g., "RunPod Access")
8. Select the scopes you need (at minimum, select "repo" for full repository access)
9. Click "Generate token"
10. **IMPORTANT**: Copy the token immediately! You won't be able to see it again.

### Step 2: Use the Token for Git Operations on RunPod

When cloning a repository, use the token as your password:

```bash
git clone https://github.com/hannesjz/my-project-name.git
# When prompted for username, enter your GitHub username
# When prompted for password, enter your personal access token
```

Alternatively, you can include the token in the URL (replace YOUR_TOKEN with your actual token):

```bash
git clone https://hannesjz:YOUR_TOKEN@github.com/hannesjz/my-project-name.git
```

### Step 3: Store Credentials to Avoid Repeated Authentication

To avoid entering your credentials every time, you can store them:

```bash
git config --global credential.helper store
# The next time you enter your credentials, they will be stored
```

## Method 2: Using SSH Keys

### Step 1: Generate an SSH Key on RunPod

```bash
# Generate a new SSH key
ssh-keygen -t ed25519 -C "your_email@example.com"

# Start the SSH agent
eval "$(ssh-agent -s)"

# Add your SSH key to the agent
ssh-add ~/.ssh/id_ed25519

# Display your public key to copy
cat ~/.ssh/id_ed25519.pub
```

### Step 2: Add the SSH Key to Your GitHub Account

1. Copy the output from the `cat ~/.ssh/id_ed25519.pub` command
2. Go to GitHub and log in to your account
3. Click on your profile picture in the top-right corner
4. Select "Settings"
5. Click on "SSH and GPG keys" in the left sidebar
6. Click "New SSH key"
7. Give your key a descriptive title (e.g., "RunPod Key")
8. Paste your public key into the "Key" field
9. Click "Add SSH key"

### Step 3: Clone the Repository Using SSH

```bash
git clone git@github.com:hannesjz/my-project-name.git
```

## Setting Up the Project on RunPod

After successfully cloning the repository, follow these steps to set up the project:

### Step 1: Navigate to the Project Directory

```bash
cd my-project-name
```

### Step 2: Create a Setup Script

```bash
cat > setup_runpod.sh << 'EOF'
#!/bin/bash
# Setup Script for Ekonomisk Rådgivare on RunPod

echo "========================================================="
echo "   Ekonomisk Rådgivare - RunPod Setup Script"
echo "========================================================="
echo

# Install Python dependencies
echo "Installing Python dependencies..."
pip install pandas openpyxl PyPDF2 nltk pdf2image pytesseract whoosh reportlab

# Download NLTK data
echo "Downloading NLTK data..."
python -c "import nltk; nltk.download('punkt'); nltk.download('stopwords')"

# Install system dependencies
echo "Installing system dependencies..."
apt-get update && apt-get install -y poppler-utils tesseract-ocr tesseract-ocr-swe

# Create directories
echo "Creating directories..."
mkdir -p data
mkdir -p test_files

# Create test files
echo "Creating test files..."
cat > test_files/test_invoice.txt << 'EOFILE'
FAKTURA

Fakturanummer: 2023-001
Datum: 2023-05-15

FRÅN:
Företag AB
Storgatan 123
123 45 Stockholm
Org.nr: 556123-4567
Tel: 08-123 45 67
E-post: info@foretagab.se

TILL:
Kund AB
Kundvägen 45
987 65 Göteborg
Org.nr: 556789-0123

BETALNINGSINFORMATION:
Bankgiro: 123-4567
Förfallodatum: 2023-06-15
Betalningsvillkor: 30 dagar

BESKRIVNING                ANTAL   PRIS      SUMMA
---------------------------------------------------------
Konsulttjänster            10 h    1 200 kr  12 000 kr
Programvaruutveckling      15 h    1 500 kr  22 500 kr
Projektledning              5 h    1 800 kr   9 000 kr
---------------------------------------------------------
                                   DELSUMMA:  43 500 kr
                                   MOMS 25%:  10 875 kr
                                   TOTALT:    54 375 kr

MEDDELANDE:
Tack för ert förtroende! Vid frågor, kontakta oss på info@foretagab.se.

Betalning ska ske senast på förfallodagen. Vid försenad betalning debiteras dröjsmålsränta enligt räntelagen.
EOFILE

cat > test_files/test_budget.csv << 'EOFILE'
Kategori,Januari,Februari,Mars,April,Maj,Juni,Totalt
Inkomst,35000,35000,35000,37500,37500,37500,217500
Hyra,9500,9500,9500,9500,9500,9500,57000
Mat,4500,4200,4800,4300,4600,4700,27100
Transport,1200,1300,1100,1400,1250,1350,7600
Nöje,2000,2500,1800,2200,2800,3000,14300
Sparande,5000,5000,5000,7000,7000,7000,36000
Övrigt,1500,1800,1600,1700,1900,1600,10100
Totala utgifter,23700,24300,23800,26100,27050,27150,152100
Kvar,11300,10700,11200,11400,10450,10350,65400
EOFILE

# Verify installation
echo "Verifying installation..."
python src/main.py

echo
echo "========================================================="
echo "   Setup Complete!"
echo "========================================================="
echo
echo "To index documents:"
echo "  python src/main.py --index /path/to/your/documents"
echo
echo "To search for documents:"
echo "  python src/main.py --search \"your search query\""
echo
echo "To view statistics:"
echo "  python src/main.py"
EOF

# Make it executable
chmod +x setup_runpod.sh
```

### Step 3: Run the Setup Script

```bash
./setup_runpod.sh
```

## Alternative: Manual Setup on RunPod

If you prefer to set up the system manually, follow these steps:

### 1. Install Python Dependencies

```bash
pip install pandas openpyxl PyPDF2 nltk pdf2image pytesseract whoosh reportlab
```

### 2. Download NLTK Data

```bash
python -c "import nltk; nltk.download('punkt'); nltk.download('stopwords')"
```

### 3. Install System Dependencies

```bash
apt-get update && apt-get install -y poppler-utils tesseract-ocr tesseract-ocr-swe
```

### 4. Create Data Directory

```bash
mkdir -p data
```

### 5. Verify Installation

```bash
python src/main.py
```

## Troubleshooting

### Common Issues on RunPod

1. **Git Authentication Failures**: Make sure you're using a personal access token or SSH key as described above.

2. **Permission Issues**: If you get permission errors when installing packages or creating directories, make sure you're running as root or using sudo.

3. **Python Version**: RunPod instances typically have multiple Python versions installed. If you encounter issues, try specifying the Python version explicitly (e.g., `python3.8` instead of `python`).

4. **Persistence**: RunPod instances may not persist data between sessions. Consider:
   - Using persistent storage volumes
   - Backing up your indexed data
   - Using Git to version control your code changes