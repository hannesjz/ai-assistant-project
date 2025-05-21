# AI Assistant with Google Cloud Storage and GitHub Integration

This project implements an AI assistant that integrates with Google Cloud Storage for document management and GitHub for code management, utilizing RunPod's high-performance computing resources.

## Architecture

The AI Assistant consists of the following components:

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

## Components

### 1. Google Cloud Storage Integration

Handles connection to and interaction with Google Cloud Storage for retrieving, storing, and updating documents.

- Authentication with Google Cloud Storage
- Listing available files and folders
- Downloading documents for processing
- Uploading processed documents and results
- Monitoring changes in cloud storage

### 2. GitHub Repository Integration

Manages connection to and interaction with GitHub for automating code updates and version control.

- Authentication with GitHub
- Repository cloning
- Change detection
- Automatic commits with descriptive messages
- Push to main branch
- Pull to keep local copy updated
- Merge conflict handling

### 3. Core AI System

Coordinates all components and manages the main workflow for the AI assistant.

- Workflow orchestration
- Task scheduling
- Processing prioritization
- Error handling and recovery
- Logging and monitoring
- API exposure for external interaction

### 4. Memory Management System

Stores and manages information about processed documents for long-term memory and contextual understanding.

- Document content and metadata storage
- Vector representation of documents
- Semantic search in memory
- Context management for related documents
- Information prioritization
- Forgetting mechanism for memory size management

### 5. Hugging Face Models Integration

Integrates and utilizes advanced language models from Hugging Face for improved document understanding and analysis.

- Model selection and loading
- Text classification
- Named entity recognition (NER)
- Document summarization
- Question answering based on document content
- Sentiment analysis
- Keyword extraction

## Setup

### Prerequisites

- Python 3.8+
- Google Cloud SDK
- Git
- Tesseract OCR
- Poppler (for PDF processing)

### Installation

1. Clone this repository:
   ```
   git clone https://github.com/yourusername/ai-assistant.git
   cd ai-assistant
   ```

2. Run the setup script:
   ```
   chmod +x setup.sh
   ./setup.sh
   ```

3. Configure the application by editing `config.json`:
   ```json
   {
     "data_dir": "./data",
     "models_dir": "./models",
     "db_path": "./data/memory.db",
     "vector_dimension": 768,
     "gcs": {
       "bucket_name": "your-bucket-name",
       "credentials_path": "/path/to/credentials.json"
     },
     "github": {
       "repo_url": "https://github.com/yourusername/your-repo.git",
       "local_path": "./repo",
       "username": "Your Name",
       "email": "your.email@example.com"
     }
   }
   ```

## Usage

### Basic Commands

```bash
# Show help
python src/ai_assistant/main.py --help

# Process a document
python src/ai_assistant/main.py --process-document /path/to/document.pdf

# Process all documents in a directory
python src/ai_assistant/main.py --process-directory /path/to/documents --recursive

# Process documents from Google Cloud Storage
python src/ai_assistant/main.py --gcs-process --gcs-prefix "documents/"

# Watch Google Cloud Storage for changes
python src/ai_assistant/main.py --gcs-watch --gcs-prefix "documents/" --gcs-interval 60

# Search for documents
python src/ai_assistant/main.py --search "your search query" --top-k 5

# Answer a question based on stored documents
python src/ai_assistant/main.py --question "What is the total revenue for Q1 2025?"

# Update code in GitHub repository
python src/ai_assistant/main.py --update-code "path/to/file.py:file content" --commit-message "Update file.py"

# Show system statistics
python src/ai_assistant/main.py --stats
```

### Using with RunPod

This AI assistant is designed to run on RunPod's high-performance computing resources. To set up on RunPod:

1. Create a RunPod instance with the following specifications:
   - 2x RTX 3090 GPUs
   - 32 vCPUs
   - 115GB RAM
   - Ubuntu 22.04 base image

2. Clone the repository and run the setup script:
   ```bash
   git clone https://github.com/yourusername/ai-assistant.git
   cd ai-assistant
   ./setup.sh
   ```

3. Configure the application with your Google Cloud Storage and GitHub credentials.

4. Run the AI assistant with the desired options.

## System Requirements

### Hardware
- RunPod with 2x RTX 3090, 32 vCPU, 115GB RAM

### Software
- Ubuntu 22.04
- Python 3.10
- CUDA 11.8
- PyTorch 2.1.0
- Google Cloud SDK
- Git

## License

This project is licensed under the MIT License - see the LICENSE file for details.
