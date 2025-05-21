#!/usr/bin/env python3
"""
Example script demonstrating how to combine semantic search with data visualization.

This script shows how to:
1. Use semantic search to find relevant documents
2. Extract metadata from these documents
3. Create visualizations based on the search results
"""

import os
import sys
from pathlib import Path

# Add the parent directory to the path so we can import the modules
sys.path.insert(0, str(Path(__file__).parent.parent))

from semantic_search.semantic_search import SemanticSearch
from data_visualization.data_visualizer import DataVisualizer

def main():
    """Main function to demonstrate semantic search and visualization."""
    # Use the data directory for semantic search
    data_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "data")
    output_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "visualizations")
    
    # Create directories if they don't exist
    os.makedirs(data_dir, exist_ok=True)
    os.makedirs(output_dir, exist_ok=True)
    
    print(f"Data directory: {data_dir}")
    print(f"Output directory: {output_dir}")
    
    # Check if there are documents in the data directory
    if not os.path.exists(os.path.join(data_dir, "metadata.json")):
        print("\nNo documents found in data directory.")
        print("Please run the following command to index some documents first:")
        print("./run_semantic.sh --index ./test_files")
        return
    
    # Initialize semantic search
    print("\nInitializing semantic search...")
    search = SemanticSearch(data_dir)
    
    # Perform semantic search
    query = "faktura"  # Example query, can be changed
    print(f"\nSearching for documents related to '{query}'...")
    results = search.search(query, semantic=True)
    
    if not results:
        print(f"No documents found for query '{query}'")
        return
    
    print(f"Found {len(results)} documents:")
    for i, (doc_id, score, metadata) in enumerate(results[:5]):
        print(f"  {i+1}. {doc_id} (score: {score:.2f})")
        if metadata:
            # Show important metadata
            important_fields = ['document_type', 'date', 'total_amount', 'supplier']
            metadata_str = ", ".join([f"{k}: {v}" for k, v in metadata.items() 
                                     if k in important_fields and v])
            if metadata_str:
                print(f"     {metadata_str}")
    
    if len(results) > 5:
        print(f"  ... and {len(results) - 5} more")
    
    # Get document clusters
    print("\nRetrieving document clusters...")
    clusters = search.get_document_clusters()
    keywords = search.get_cluster_keywords()
    
    print(f"Documents are clustered into {len(clusters)} groups:")
    for cluster_id, doc_ids in list(clusters.items())[:3]:
        print(f"  Cluster {cluster_id} ({len(doc_ids)} documents):")
        if cluster_id in keywords:
            print(f"    Keywords: {', '.join(keywords[cluster_id])}")
        print(f"    Documents: {', '.join(doc_ids[:3])}{'...' if len(doc_ids) > 3 else ''}")
    
    if len(clusters) > 3:
        print(f"  ... and {len(clusters) - 3} more clusters")
    
    # Get entities
    print("\nRetrieving extracted entities...")
    entities = search.get_entities()
    
    for entity_type, entity_set in entities.items():
        print(f"  {entity_type.capitalize()}: {len(entity_set)}")
        if entity_set:
            print(f"    Examples: {', '.join(list(entity_set)[:3])}")
    
    # Initialize data visualizer
    print("\nInitializing data visualizer...")
    visualizer = DataVisualizer(data_dir, output_dir)
    
    # Create visualizations
    print("\nCreating visualizations...")
    
    # Time series plot
    print("  Creating time series plot...")
    time_series_plot = visualizer.plot_time_series()
    if time_series_plot:
        print(f"    Saved to: {time_series_plot}")
    
    # Interactive time series plot
    print("  Creating interactive time series plot...")
    interactive_time_series = visualizer.plot_interactive_time_series()
    if interactive_time_series:
        print(f"    Saved to: {interactive_time_series}")
    
    # Supplier distribution plot
    print("  Creating supplier distribution plot...")
    supplier_plot = visualizer.plot_supplier_distribution()
    if supplier_plot:
        print(f"    Saved to: {supplier_plot}")
    
    # Interactive supplier distribution plot
    print("  Creating interactive supplier distribution plot...")
    interactive_supplier = visualizer.plot_interactive_supplier_distribution()
    if interactive_supplier:
        print(f"    Saved to: {interactive_supplier}")
    
    # Document type distribution plot
    print("  Creating document type distribution plot...")
    doc_type_plot = visualizer.plot_document_type_distribution()
    if doc_type_plot:
        print(f"    Saved to: {doc_type_plot}")
    
    # Interactive document type distribution plot
    print("  Creating interactive document type distribution plot...")
    interactive_doc_type = visualizer.plot_interactive_document_type_distribution()
    if interactive_doc_type:
        print(f"    Saved to: {interactive_doc_type}")
    
    # Export data summary
    print("\nExporting data summary...")
    summary = visualizer.export_data_summary()
    if summary:
        print(f"  Saved to: {summary}")
    
    print("\nAll operations completed successfully!")
    print(f"Visualizations are available in: {output_dir}")
    print("You can open the HTML files in a web browser to interact with the visualizations.")

if __name__ == "__main__":
    main()