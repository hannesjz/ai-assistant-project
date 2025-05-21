"""
Test module for the DataVisualizer class.
"""

import os
import sys
import unittest
from pathlib import Path

# Add the parent directory to the path so we can import the modules
sys.path.insert(0, str(Path(__file__).parent.parent))

from data_visualization.data_visualizer import DataVisualizer

class TestDataVisualizer(unittest.TestCase):
    """Test cases for the DataVisualizer class."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Use the processed_docs directory for testing
        self.data_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "processed_docs")
        self.output_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "visualizations")
        
        # Create DataVisualizer instance
        self.visualizer = DataVisualizer(self.data_dir, self.output_dir)
    
    def test_create_dashboard(self):
        """Test creating a dashboard with multiple visualizations."""
        # Create a dashboard
        plots = self.visualizer.create_dashboard()
        
        # Check if plots were created
        self.assertIsInstance(plots, list)
        print(f"Created {len(plots)} plots")
        for plot in plots:
            print(f"  - {plot}")
    
    def test_interactive_visualizations(self):
        """Test creating interactive visualizations."""
        # Create interactive time series plot
        time_series_plot = self.visualizer.plot_interactive_time_series()
        if time_series_plot:
            print(f"Created interactive time series plot: {time_series_plot}")
        
        # Create interactive supplier distribution plot
        supplier_plot = self.visualizer.plot_interactive_supplier_distribution()
        if supplier_plot:
            print(f"Created interactive supplier distribution plot: {supplier_plot}")
        
        # Create interactive document type distribution plot
        doc_type_plot = self.visualizer.plot_interactive_document_type_distribution()
        if doc_type_plot:
            print(f"Created interactive document type distribution plot: {doc_type_plot}")
        
        # Create interactive seasonal variation plot
        seasonal_plot = self.visualizer.plot_interactive_seasonal_variation()
        if seasonal_plot:
            print(f"Created interactive seasonal variation plot: {seasonal_plot}")

if __name__ == "__main__":
    unittest.main()