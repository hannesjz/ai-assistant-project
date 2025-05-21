# Semantic Search for Ekonomisk Rådgivare

This module adds advanced semantic search capabilities to the Ekonomisk Rådgivare system, allowing for more intelligent document search, analysis, and visualization.

## Features

- **Semantic Search**: Find documents based on meaning, not just exact keyword matches
- **Fuzzy Search**: Find documents even with misspelled or variant terms
- **Document Clustering**: Automatically group similar documents together
- **Entity Recognition**: Extract companies, people, amounts, and dates from documents
- **Trend Analysis**: Analyze trends in financial data over time
- **Related Terms**: Find terms that frequently appear together in documents

## Requirements

The semantic search functionality requires additional dependencies:

```
nltk>=3.6.0
scikit-learn>=1.0.0
numpy>=1.20.0
spacy>=3.0.0
```

For optimal performance with Swedish documents, install the Swedish language model for spaCy:

```bash
python -m spacy download sv_core_news_sm
```

## Usage

The semantic search functionality can be accessed through the `run_semantic.sh` script, which provides a convenient command-line interface.

### Basic Usage

```bash
# Index documents in a directory
./run_semantic.sh --index ./test_files

# Search for documents
./run_semantic.sh --search "faktura" --semantic

# Filter by document type
./run_semantic.sh --search "belopp" --type invoice

# Show document clusters
./run_semantic.sh --cluster

# Show extracted entities
./run_semantic.sh --entities

# Find related terms
./run_semantic.sh --related "faktura"

# Analyze trends
./run_semantic.sh --trends total_amount --group-by date

# Full document analysis
./run_semantic.sh --analyze

# Save results to file
./run_semantic.sh --search "faktura" --output results.txt
```

### Command-Line Options

- `--index DIR`: Index files in directory
- `--search QUERY`: Search for documents
- `--fuzzy`: Use fuzzy search
- `--semantic`: Use semantic search
- `--analyze`: Analyze documents
- `--type TYPE`: Filter by document type (invoice, receipt, etc.)
- `--cluster`: Show document clusters
- `--entities`: Show extracted entities
- `--trends FIELD`: Analyze trends in field (e.g., total_amount)
- `--group-by FIELD`: Field to group by for trend analysis (default: date)
- `--related TERM`: Show terms related to input term
- `--output FILE`: Save results to file
- `--help`: Show help message

## Integration with Data Visualization

The semantic search functionality can be combined with the data visualization module to create powerful insights:

1. Use semantic search to find relevant documents
2. Extract metadata from these documents
3. Use the DataVisualizer class to create visualizations based on this metadata

Example:

```python
from semantic_search.semantic_search import SemanticSearch
from data_visualization.data_visualizer import DataVisualizer

# Initialize semantic search
search = SemanticSearch("./data")

# Search for documents
results = search.search("faktura", semantic=True)

# Extract document IDs
doc_ids = [doc_id for doc_id, _, _ in results]

# Initialize data visualizer
visualizer = DataVisualizer("./data", "./visualizations")

# Create visualizations for the search results
visualizer.plot_interactive_time_series()
visualizer.plot_interactive_supplier_distribution()
```

## How It Works

The semantic search functionality works by:

1. **Indexing**: Documents are processed and converted to vector representations using TF-IDF
2. **Clustering**: Documents are grouped into clusters using K-means clustering
3. **Entity Recognition**: Entities are extracted using regex patterns or spaCy NER
4. **Search**: Queries are processed and matched against documents using cosine similarity
5. **Analysis**: Trends and patterns are analyzed using statistical methods

## Extending the Functionality

The semantic search functionality can be extended in several ways:

- Add support for more languages
- Implement more advanced NLP techniques (e.g., word embeddings, transformers)
- Add more visualization types
- Integrate with external APIs for additional data sources