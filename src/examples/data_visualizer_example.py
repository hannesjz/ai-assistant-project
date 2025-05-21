#!/usr/bin/env python3
"""
Example script demonstrating how to use the DataVisualizer class.

This script creates both static and interactive visualizations for financial data.
"""

import os
import sys
from pathlib import Path

# Add the parent directory to the path so we can import the modules
sys.path.insert(0, str(Path(__file__).parent.parent))

from data_visualization.data_visualizer import DataVisualizer

def main():
    """Main function to demonstrate DataVisualizer usage."""
    # Use the processed_docs directory for testing
    data_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "processed_docs")
    output_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "visualizations")
    
    print(f"Data directory: {data_dir}")
    print(f"Output directory: {output_dir}")
    
    # Create DataVisualizer instance
    visualizer = DataVisualizer(data_dir, output_dir)
    
    # Create static visualizations
    print("\nCreating static visualizations...")
    
    # Time series plot
    time_series_plot = visualizer.plot_time_series()
    if time_series_plot:
        print(f"  - Created time series plot: {time_series_plot}")
    
    # Supplier distribution plot
    supplier_plot = visualizer.plot_supplier_distribution()
    if supplier_plot:
        print(f"  - Created supplier distribution plot: {supplier_plot}")
    
    # Document type distribution plot
    doc_type_plot = visualizer.plot_document_type_distribution()
    if doc_type_plot:
        print(f"  - Created document type distribution plot: {doc_type_plot}")
    
    # Seasonal variation plot
    seasonal_plot = visualizer.plot_seasonal_variation()
    if seasonal_plot:
        print(f"  - Created seasonal variation plot: {seasonal_plot}")
    
    # Amount distribution plot
    amount_plot = visualizer.plot_amount_distribution()
    if amount_plot:
        print(f"  - Created amount distribution plot: {amount_plot}")
    
    # Create interactive visualizations
    print("\nCreating interactive visualizations...")
    
    # Interactive time series plot
    interactive_time_series = visualizer.plot_interactive_time_series()
    if interactive_time_series:
        print(f"  - Created interactive time series plot: {interactive_time_series}")
    
    # Interactive supplier distribution plot
    interactive_supplier = visualizer.plot_interactive_supplier_distribution()
    if interactive_supplier:
        print(f"  - Created interactive supplier distribution plot: {interactive_supplier}")
    
    # Interactive document type distribution plot
    interactive_doc_type = visualizer.plot_interactive_document_type_distribution()
    if interactive_doc_type:
        print(f"  - Created interactive document type distribution plot: {interactive_doc_type}")
    
    # Interactive seasonal variation plot
    interactive_seasonal = visualizer.plot_interactive_seasonal_variation()
    if interactive_seasonal:
        print(f"  - Created interactive seasonal variation plot: {interactive_seasonal}")
    
    # Interactive amount distribution plot
    interactive_amount = visualizer.plot_interactive_amount_distribution()
    if interactive_amount:
        print(f"  - Created interactive amount distribution plot: {interactive_amount}")
    
    # Export data summary
    summary = visualizer.export_data_summary()
    if summary:
        print(f"\nExported data summary to: {summary}")
    
    print("\nAll visualizations have been created successfully!")

if __name__ == "__main__":
    main()