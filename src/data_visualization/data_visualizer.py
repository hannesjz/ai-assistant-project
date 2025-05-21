"""
Data Visualization Module for Ekonomisk Rådgivare

This module provides visualization capabilities for financial data:
1. Time series analysis of financial metrics
2. Supplier distribution and spending patterns
3. Document type distribution
4. Seasonal variations in expenses
5. Interactive visualizations

Dependencies:
- matplotlib
- seaborn
- plotly
- pandas
- numpy
"""

import os
import json
import logging
import numpy as np
import pandas as pd
from typing import Dict, List, Any, Optional, Tuple, Union
from pathlib import Path
from datetime import datetime
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from collections import Counter

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class DataVisualizer:
    """Class for visualizing financial data from documents."""
    
    def __init__(self, data_dir: str, output_dir: str = "./visualizations"):
        """
        Initialize the Data Visualizer.
        
        Args:
            data_dir (str): Directory containing indexed data
            output_dir (str): Directory to save visualizations
        """
        self.data_dir = data_dir
        self.output_dir = output_dir
        self.metadata = {}
        self.df = None
        
        # Create output directory if it doesn't exist
        os.makedirs(output_dir, exist_ok=True)
        
        # Set up visualization style
        self._setup_visualization_style()
        
        # Load metadata
        self._load_metadata()
        
        # Convert metadata to DataFrame
        self._create_dataframe()
    
    def _setup_visualization_style(self) -> None:
        """Set up visualization style."""
        # Set Seaborn style
        sns.set(style="whitegrid")
        sns.set_palette("colorblind")
        
        # Set Matplotlib params
        plt.rcParams['figure.figsize'] = (12, 8)
        plt.rcParams['font.size'] = 12
        plt.rcParams['axes.labelsize'] = 14
        plt.rcParams['axes.titlesize'] = 16
        plt.rcParams['xtick.labelsize'] = 12
        plt.rcParams['ytick.labelsize'] = 12
    
    def _load_metadata(self) -> None:
        """Load metadata from data directory."""
        metadata_file = os.path.join(self.data_dir, "metadata.json")
        if not os.path.exists(metadata_file):
            logger.error(f"Metadata file not found: {metadata_file}")
            return
        
        try:
            with open(metadata_file, 'r') as f:
                self.metadata = json.load(f)
            logger.info(f"Loaded metadata for {len(self.metadata)} documents")
        except Exception as e:
            logger.error(f"Error loading metadata: {e}")
    
    def _create_dataframe(self) -> None:
        """Convert metadata to DataFrame for analysis."""
        if not self.metadata:
            logger.warning("No metadata available for analysis")
            return
        
        # Extract data from metadata
        data = []
        for doc_id, metadata in self.metadata.items():
            # Create a record with basic fields
            record = {
                'document_id': doc_id,
                'document_type': metadata.get('document_type', 'unknown'),
                'supplier': metadata.get('supplier', 'unknown'),
                'total_amount': None,
                'date': None,
                'year': None,
                'month': None,
                'quarter': None
            }
            
            # Extract and convert amount
            if 'total_amount' in metadata:
                try:
                    amount = metadata['total_amount']
                    if isinstance(amount, str):
                        # Remove non-numeric characters and convert to float
                        amount = amount.replace(' ', '').replace(',', '.')
                        amount = ''.join(c for c in amount if c.isdigit() or c == '.')
                        amount = float(amount)
                    record['total_amount'] = amount
                except:
                    pass
            
            # Extract and convert date
            if 'date' in metadata:
                try:
                    date_str = metadata['date']
                    # Try different date formats
                    for fmt in ['%Y-%m-%d', '%d/%m/%Y', '%d.%m.%Y']:
                        try:
                            date_obj = datetime.strptime(date_str, fmt)
                            record['date'] = date_obj
                            record['year'] = date_obj.year
                            record['month'] = date_obj.month
                            record['quarter'] = (date_obj.month - 1) // 3 + 1
                            break
                        except ValueError:
                            continue
                except:
                    pass
            
            # Add record to data
            data.append(record)
        
        # Create DataFrame
        self.df = pd.DataFrame(data)
        logger.info(f"Created DataFrame with {len(self.df)} records")
    
    def plot_time_series(self, field: str = 'total_amount', 
                        group_by: str = 'month', 
                        document_type: Optional[str] = None,
                        save: bool = True) -> str:
        """
        Plot time series of financial metrics.
        
        Args:
            field (str): Field to plot
            group_by (str): Time unit to group by ('day', 'month', 'quarter', 'year')
            document_type (str): Type of documents to include
            save (bool): Whether to save the plot to file
            
        Returns:
            str: Path to saved plot or empty string if not saved
        """
        if self.df is None or self.df.empty:
            logger.warning("No data available for time series plot")
            return ""
        
        # Filter by document type if specified
        df = self.df
        if document_type:
            df = df[df['document_type'] == document_type]
            if df.empty:
                logger.warning(f"No documents of type '{document_type}' found")
                return ""
        
        # Check if field exists
        if field not in df.columns:
            logger.warning(f"Field '{field}' not found in data")
            return ""
        
        # Check if date column exists
        if 'date' not in df.columns or df['date'].isna().all():
            logger.warning("No date information available for time series plot")
            return ""
        
        # Group data
        if group_by == 'day':
            df['group'] = df['date'].dt.date
        elif group_by == 'month':
            df['group'] = df['date'].dt.to_period('M')
        elif group_by == 'quarter':
            df['group'] = df['date'].dt.to_period('Q')
        elif group_by == 'year':
            df['group'] = df['date'].dt.year
        else:
            logger.warning(f"Invalid group_by value: {group_by}")
            return ""
        
        # Aggregate data
        grouped = df.groupby('group')[field].agg(['sum', 'mean', 'count']).reset_index()
        
        # Sort by date
        grouped = grouped.sort_values('group')
        
        # Create figure
        fig, ax1 = plt.subplots()
        
        # Plot sum as bars
        ax1.bar(range(len(grouped)), grouped['sum'], alpha=0.7, color='steelblue')
        ax1.set_ylabel(f'Sum of {field}', color='steelblue')
        ax1.tick_params(axis='y', labelcolor='steelblue')
        
        # Create second y-axis for count
        ax2 = ax1.twinx()
        ax2.plot(range(len(grouped)), grouped['count'], 'r-', linewidth=2)
        ax2.set_ylabel('Number of documents', color='red')
        ax2.tick_params(axis='y', labelcolor='red')
        
        # Set x-axis labels
        plt.xticks(range(len(grouped)), [str(g) for g in grouped['group']], rotation=45)
        
        # Set title and labels
        title = f"{field.capitalize()} by {group_by}"
        if document_type:
            title += f" for {document_type} documents"
        plt.title(title)
        plt.tight_layout()
        
        # Save plot if requested
        if save:
            filename = f"time_series_{field}_by_{group_by}"
            if document_type:
                filename += f"_{document_type}"
            filename += ".png"
            filepath = os.path.join(self.output_dir, filename)
            plt.savefig(filepath)
            logger.info(f"Saved time series plot to {filepath}")
            plt.close()
            return filepath
        else:
            plt.show()
            plt.close()
            return ""
    
    def plot_interactive_time_series(self, field: str = 'total_amount', 
                                   group_by: str = 'month', 
                                   document_type: Optional[str] = None,
                                   save: bool = True) -> str:
        """
        Create an interactive time series plot using Plotly.
        
        Args:
            field (str): Field to plot
            group_by (str): Time unit to group by ('day', 'month', 'quarter', 'year')
            document_type (str): Type of documents to include
            save (bool): Whether to save the plot to file
            
        Returns:
            str: Path to saved plot or empty string if not saved
        """
        if self.df is None or self.df.empty:
            logger.warning("No data available for interactive time series plot")
            return ""
        
        # Filter by document type if specified
        df = self.df
        if document_type:
            df = df[df['document_type'] == document_type]
            if df.empty:
                logger.warning(f"No documents of type '{document_type}' found")
                return ""
        
        # Check if field exists
        if field not in df.columns:
            logger.warning(f"Field '{field}' not found in data")
            return ""
        
        # Check if date column exists
        if 'date' not in df.columns or df['date'].isna().all():
            logger.warning("No date information available for time series plot")
            return ""
        
        # Group data
        if group_by == 'day':
            df['group'] = df['date'].dt.date
        elif group_by == 'month':
            df['group'] = df['date'].dt.to_period('M').astype(str)
        elif group_by == 'quarter':
            df['group'] = df['date'].dt.to_period('Q').astype(str)
        elif group_by == 'year':
            df['group'] = df['date'].dt.year
        else:
            logger.warning(f"Invalid group_by value: {group_by}")
            return ""
        
        # Aggregate data
        grouped = df.groupby('group')[field].agg(['sum', 'mean', 'count']).reset_index()
        
        # Sort by date
        grouped = grouped.sort_values('group')
        
        # Create interactive figure with Plotly
        fig = make_subplots(specs=[[{"secondary_y": True}]])
        
        # Add bar chart for sum
        fig.add_trace(
            go.Bar(
                x=grouped['group'],
                y=grouped['sum'],
                name=f'Sum of {field}',
                marker_color='steelblue',
                hovertemplate='%{x}<br>Sum: %{y:.2f}<extra></extra>'
            ),
            secondary_y=False
        )
        
        # Add line chart for count
        fig.add_trace(
            go.Scatter(
                x=grouped['group'],
                y=grouped['count'],
                name='Number of documents',
                line=dict(color='red', width=3),
                hovertemplate='%{x}<br>Count: %{y}<extra></extra>'
            ),
            secondary_y=True
        )
        
        # Set title and labels
        title = f"{field.capitalize()} by {group_by}"
        if document_type:
            title += f" for {document_type} documents"
            
        fig.update_layout(
            title=title,
            hovermode="x unified",
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1
            )
        )
        
        # Set y-axes titles
        fig.update_yaxes(title_text=f"Sum of {field}", secondary_y=False)
        fig.update_yaxes(title_text="Number of documents", secondary_y=True)
        
        # Save plot if requested
        if save:
            filename = f"interactive_time_series_{field}_by_{group_by}"
            if document_type:
                filename += f"_{document_type}"
            filename += ".html"
            filepath = os.path.join(self.output_dir, filename)
            fig.write_html(filepath)
            logger.info(f"Saved interactive time series plot to {filepath}")
            return filepath
        else:
            fig.show()
            return ""
    
    def plot_supplier_distribution(self, top_n: int = 10, 
                                 by_amount: bool = True,
                                 document_type: Optional[str] = None,
                                 save: bool = True) -> str:
        """
        Plot distribution of suppliers.
        
        Args:
            top_n (int): Number of top suppliers to include
            by_amount (bool): Whether to rank by amount (True) or count (False)
            document_type (str): Type of documents to include
            save (bool): Whether to save the plot to file
            
        Returns:
            str: Path to saved plot or empty string if not saved
        """
        if self.df is None or self.df.empty:
            logger.warning("No data available for supplier distribution plot")
            return ""
        
        # Filter by document type if specified
        df = self.df
        if document_type:
            df = df[df['document_type'] == document_type]
            if df.empty:
                logger.warning(f"No documents of type '{document_type}' found")
                return ""
        
        # Check if supplier column exists
        if 'supplier' not in df.columns or df['supplier'].isna().all():
            logger.warning("No supplier information available for distribution plot")
            return ""
        
        # Group by supplier
        if by_amount:
            # Check if total_amount column exists
            if 'total_amount' not in df.columns or df['total_amount'].isna().all():
                logger.warning("No amount information available for distribution plot")
                return ""
            
            # Group by supplier and sum amounts
            grouped = df.groupby('supplier')['total_amount'].sum().reset_index()
            grouped = grouped.sort_values('total_amount', ascending=False)
            value_col = 'total_amount'
            ylabel = 'Total amount'
        else:
            # Group by supplier and count documents
            grouped = df.groupby('supplier').size().reset_index(name='count')
            grouped = grouped.sort_values('count', ascending=False)
            value_col = 'count'
            ylabel = 'Number of documents'
        
        # Take top N suppliers
        grouped = grouped.head(top_n)
        
        # Create horizontal bar chart
        plt.figure(figsize=(12, 8))
        bars = plt.barh(grouped['supplier'], grouped[value_col], color='steelblue')
        
        # Add values to bars
        for i, bar in enumerate(bars):
            plt.text(bar.get_width() + (bar.get_width() * 0.01), 
                    bar.get_y() + bar.get_height()/2, 
                    f"{grouped[value_col].iloc[i]:,.0f}", 
                    va='center')
        
        # Set title and labels
        title = f"Top {top_n} suppliers by {'amount' if by_amount else 'document count'}"
        if document_type:
            title += f" for {document_type} documents"
        plt.title(title)
        plt.xlabel(ylabel)
        plt.ylabel('Supplier')
        plt.tight_layout()
        
        # Save plot if requested
        if save:
            filename = f"supplier_distribution_by_{'amount' if by_amount else 'count'}"
            if document_type:
                filename += f"_{document_type}"
            filename += ".png"
            filepath = os.path.join(self.output_dir, filename)
            plt.savefig(filepath)
            logger.info(f"Saved supplier distribution plot to {filepath}")
            plt.close()
            return filepath
        else:
            plt.show()
            plt.close()
            return ""
    
    def plot_interactive_supplier_distribution(self, top_n: int = 10, 
                                             by_amount: bool = True,
                                             document_type: Optional[str] = None,
                                             save: bool = True) -> str:
        """
        Create an interactive supplier distribution plot using Plotly.
        
        Args:
            top_n (int): Number of top suppliers to include
            by_amount (bool): Whether to rank by amount (True) or count (False)
            document_type (str): Type of documents to include
            save (bool): Whether to save the plot to file
            
        Returns:
            str: Path to saved plot or empty string if not saved
        """
        if self.df is None or self.df.empty:
            logger.warning("No data available for interactive supplier distribution plot")
            return ""
        
        # Filter by document type if specified
        df = self.df
        if document_type:
            df = df[df['document_type'] == document_type]
            if df.empty:
                logger.warning(f"No documents of type '{document_type}' found")
                return ""
        
        # Check if supplier column exists
        if 'supplier' not in df.columns or df['supplier'].isna().all():
            logger.warning("No supplier information available for distribution plot")
            return ""
        
        # Group by supplier
        if by_amount:
            # Check if total_amount column exists
            if 'total_amount' not in df.columns or df['total_amount'].isna().all():
                logger.warning("No amount information available for distribution plot")
def plot_document_type_distribution(self, by_amount: bool = False,
                                      save: bool = True) -> str:
        """
        Plot distribution of document types.
        
        Args:
            by_amount (bool): Whether to show distribution by amount (True) or count (False)
            save (bool): Whether to save the plot to file
            
        Returns:
            str: Path to saved plot or empty string if not saved
        """
        if self.df is None or self.df.empty:
            logger.warning("No data available for document type distribution plot")
            return ""
        
        # Check if document_type column exists
        if 'document_type' not in self.df.columns:
            logger.warning("No document type information available for distribution plot")
            return ""
        
        # Group by document type
        if by_amount:
            # Check if total_amount column exists
            if 'total_amount' not in self.df.columns or self.df['total_amount'].isna().all():
                logger.warning("No amount information available for distribution plot")
                return ""
            
            # Group by document type and sum amounts
            grouped = self.df.groupby('document_type')['total_amount'].sum().reset_index()
            value_col = 'total_amount'
            ylabel = 'Total amount'
        else:
            # Group by document type and count documents
            grouped = self.df.groupby('document_type').size().reset_index(name='count')
            value_col = 'count'
            ylabel = 'Number of documents'
        
        # Sort by value
        grouped = grouped.sort_values(value_col, ascending=False)
        
        # Create pie chart
        plt.figure(figsize=(10, 10))
        plt.pie(grouped[value_col], labels=grouped['document_type'], autopct='%1.1f%%',
               shadow=True, startangle=90)
        plt.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle
        
        # Set title
        title = f"Document type distribution by {'amount' if by_amount else 'count'}"
        plt.title(title)
        plt.tight_layout()
        
        # Save plot if requested
        if save:
            filename = f"document_type_distribution_by_{'amount' if by_amount else 'count'}.png"
            filepath = os.path.join(self.output_dir, filename)
            plt.savefig(filepath)
            logger.info(f"Saved document type distribution plot to {filepath}")
            plt.close()
            return filepath
        else:
            plt.show()
            plt.close()
            return ""
    
    def plot_interactive_document_type_distribution(self, by_amount: bool = False,
                                                 save: bool = True) -> str:
        """
        Create an interactive document type distribution plot using Plotly.
        
        Args:
            by_amount (bool): Whether to show distribution by amount (True) or count (False)
            save (bool): Whether to save the plot to file
            
        Returns:
            str: Path to saved plot or empty string if not saved
        """
        if self.df is None or self.df.empty:
            logger.warning("No data available for interactive document type distribution plot")
            return ""
        
        # Check if document_type column exists
        if 'document_type' not in self.df.columns:
            logger.warning("No document type information available for distribution plot")
            return ""
        
        # Group by document type
        if by_amount:
            # Check if total_amount column exists
            if 'total_amount' not in self.df.columns or self.df['total_amount'].isna().all():
                logger.warning("No amount information available for distribution plot")
                return ""
            
            # Group by document type and sum amounts
            grouped = self.df.groupby('document_type')['total_amount'].sum().reset_index()
            value_col = 'total_amount'
            title_suffix = 'amount'
        else:
            # Group by document type and count documents
            grouped = self.df.groupby('document_type').size().reset_index(name='count')
            value_col = 'count'
            title_suffix = 'count'
        
        # Sort by value
        grouped = grouped.sort_values(value_col, ascending=False)
        
        # Create interactive pie chart with Plotly
        fig = px.pie(
            grouped, 
            values=value_col, 
            names='document_type',
            title=f"Document type distribution by {title_suffix}",
            hover_data=[value_col],
            labels={'document_type': 'Document Type'},
            color_discrete_sequence=px.colors.qualitative.Plotly
        )
        
        # Update layout
        fig.update_traces(
            textposition='inside', 
            textinfo='percent+label',
            hovertemplate='<b>%{label}</b><br>%{value:.2f}<br>%{percent}'
        )
        
        # Save plot if requested
        if save:
            filename = f"interactive_document_type_distribution_by_{title_suffix}.html"
            filepath = os.path.join(self.output_dir, filename)
            fig.write_html(filepath)
            logger.info(f"Saved interactive document type distribution plot to {filepath}")
            return filepath
        else:
            fig.show()
            return ""
    
    def plot_seasonal_variation(self, field: str = 'total_amount',
                              document_type: Optional[str] = None,
                              save: bool = True) -> str:
        """
        Plot seasonal variation of financial metrics.
        
        Args:
            field (str): Field to plot
            document_type (str): Type of documents to include
            save (bool): Whether to save the plot to file
            
        Returns:
            str: Path to saved plot or empty string if not saved
        """
        if self.df is None or self.df.empty:
            logger.warning("No data available for seasonal variation plot")
            return ""
        
        # Filter by document type if specified
        df = self.df
        if document_type:
            df = df[df['document_type'] == document_type]
            if df.empty:
                logger.warning(f"No documents of type '{document_type}' found")
                return ""
        
        # Check if field exists
        if field not in df.columns:
            logger.warning(f"Field '{field}' not found in data")
            return ""
        
        # Check if date column exists
        if 'date' not in df.columns or df['date'].isna().all():
            logger.warning("No date information available for seasonal variation plot")
            return ""
        
        # Extract month and year
        df['month'] = df['date'].dt.month
        df['year'] = df['date'].dt.year
        
        # Group by month and year
        grouped = df.groupby(['year', 'month'])[field].agg(['sum', 'mean', 'count']).reset_index()
        
        # Create pivot table for heatmap
        pivot = grouped.pivot(index='month', columns='year', values='sum')
        
        # Create heatmap
        plt.figure(figsize=(12, 8))
        sns.heatmap(pivot, annot=True, fmt=".0f", cmap="YlGnBu", linewidths=.5)
        
        # Set title and labels
        title = f"Seasonal variation of {field}"
        if document_type:
            title += f" for {document_type} documents"
        plt.title(title)
        plt.xlabel('Year')
        plt.ylabel('Month')
        
        # Set month labels
        month_labels = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 
                       'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
        plt.yticks(np.arange(0.5, 12.5), month_labels)
        
        plt.tight_layout()
        
        # Save plot if requested
        if save:
            filename = f"seasonal_variation_{field}"
            if document_type:
                filename += f"_{document_type}"
            filename += ".png"
            filepath = os.path.join(self.output_dir, filename)
            plt.savefig(filepath)
            logger.info(f"Saved seasonal variation plot to {filepath}")
            plt.close()
            return filepath
        else:
            plt.show()
            plt.close()
            return ""
    
    def plot_interactive_seasonal_variation(self, field: str = 'total_amount',
                                          document_type: Optional[str] = None,
                                          save: bool = True) -> str:
        """
        Create an interactive seasonal variation plot using Plotly.
        
        Args:
            field (str): Field to plot
            document_type (str): Type of documents to include
            save (bool): Whether to save the plot to file
            
        Returns:
            str: Path to saved plot or empty string if not saved
        """
        if self.df is None or self.df.empty:
            logger.warning("No data available for interactive seasonal variation plot")
            return ""
        
        # Filter by document type if specified
        df = self.df
        if document_type:
            df = df[df['document_type'] == document_type]
            if df.empty:
                logger.warning(f"No documents of type '{document_type}' found")
                return ""
        
        # Check if field exists
        if field not in df.columns:
            logger.warning(f"Field '{field}' not found in data")
            return ""
        
        # Check if date column exists
        if 'date' not in df.columns or df['date'].isna().all():
            logger.warning("No date information available for seasonal variation plot")
            return ""
        
        # Extract month and year
        df['month'] = df['date'].dt.month
        df['year'] = df['date'].dt.year
        
        # Group by month and year
        grouped = df.groupby(['year', 'month'])[field].agg(['sum', 'mean', 'count']).reset_index()
        
        # Create pivot table for heatmap
        pivot = grouped.pivot(index='month', columns='year', values='sum')
        
        # Convert pivot table to format suitable for Plotly
        z_data = pivot.values.tolist()
        x_data = pivot.columns.tolist()
        y_data = pivot.index.tolist()
        
        # Create month labels
        month_labels = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 
                       'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
        
        # Create interactive heatmap with Plotly
        fig = go.Figure(data=go.Heatmap(
            z=z_data,
            x=x_data,
            y=[month_labels[m-1] for m in y_data],
            hoverongaps=False,
            colorscale='Blues',
            hovertemplate='Year: %{x}<br>Month: %{y}<br>Value: %{z:,.2f}<extra></extra>'
        ))
        
        # Set title and labels
        title = f"Seasonal variation of {field}"
        if document_type:
            title += f" for {document_type} documents"
            
        fig.update_layout(
            title=title,
            xaxis_title='Year',
            yaxis_title='Month',
            yaxis=dict(
                tickmode='array',
                tickvals=list(range(len(y_data))),
                ticktext=[month_labels[m-1] for m in y_data]
            )
        )
        
        # Save plot if requested
        if save:
            filename = f"interactive_seasonal_variation_{field}"
            if document_type:
                filename += f"_{document_type}"
            filename += ".html"
            filepath = os.path.join(self.output_dir, filename)
            fig.write_html(filepath)
            logger.info(f"Saved interactive seasonal variation plot to {filepath}")
            return filepath
        else:
            fig.show()
            return ""
    
    def plot_amount_distribution(self, bins: int = 20,
                               document_type: Optional[str] = None,
                               save: bool = True) -> str:
        """
        Plot distribution of amounts.
        
        Args:
            bins (int): Number of bins for histogram
            document_type (str): Type of documents to include
            save (bool): Whether to save the plot to file
            
        Returns:
            str: Path to saved plot or empty string if not saved
        """
        if self.df is None or self.df.empty:
            logger.warning("No data available for amount distribution plot")
            return ""
        
        # Filter by document type if specified
        df = self.df
        if document_type:
            df = df[df['document_type'] == document_type]
            if df.empty:
                logger.warning(f"No documents of type '{document_type}' found")
                return ""
        
        # Check if total_amount column exists
        if 'total_amount' not in df.columns or df['total_amount'].isna().all():
            logger.warning("No amount information available for distribution plot")
            return ""
        
        # Create figure with two subplots
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 8))
        
        # Plot histogram
        sns.histplot(df['total_amount'].dropna(), bins=bins, kde=True, ax=ax1)
        ax1.set_title('Amount distribution')
        ax1.set_xlabel('Amount')
        ax1.set_ylabel('Frequency')
        
        # Plot box plot
        sns.boxplot(y=df['total_amount'].dropna(), ax=ax2)
        ax2.set_title('Amount box plot')
        ax2.set_ylabel('Amount')
        
        # Set overall title
        title = "Distribution of amounts"
        if document_type:
            title += f" for {document_type} documents"
        fig.suptitle(title, fontsize=16)
        
        plt.tight_layout()
        plt.subplots_adjust(top=0.9)
        
        # Save plot if requested
        if save:
            filename = f"amount_distribution"
            if document_type:
                filename += f"_{document_type}"
            filename += ".png"
            filepath = os.path.join(self.output_dir, filename)
            plt.savefig(filepath)
            logger.info(f"Saved amount distribution plot to {filepath}")
            plt.close()
            return filepath
        else:
            plt.show()
            plt.close()
            return ""
    
    def plot_interactive_amount_distribution(self, bins: int = 20,
                                           document_type: Optional[str] = None,
                                           save: bool = True) -> str:
        """
        Create an interactive amount distribution plot using Plotly.
        
        Args:
            bins (int): Number of bins for histogram
            document_type (str): Type of documents to include
            save (bool): Whether to save the plot to file
            
        Returns:
            str: Path to saved plot or empty string if not saved
        """
        if self.df is None or self.df.empty:
            logger.warning("No data available for interactive amount distribution plot")
            return ""
        
        # Filter by document type if specified
        df = self.df
        if document_type:
            df = df[df['document_type'] == document_type]
            if df.empty:
                logger.warning(f"No documents of type '{document_type}' found")
                return ""
        
        # Check if total_amount column exists
        if 'total_amount' not in df.columns or df['total_amount'].isna().all():
            logger.warning("No amount information available for distribution plot")
            return ""
        
        # Create interactive figure with Plotly
        fig = make_subplots(rows=1, cols=2, 
                           subplot_titles=('Amount Distribution', 'Amount Box Plot'),
                           specs=[[{"type": "histogram"}, {"type": "box"}]])
        
        # Add histogram
        fig.add_trace(
            go.Histogram(
                x=df['total_amount'].dropna(),
                nbinsx=bins,
                name='Amount',
                marker_color='steelblue',
                opacity=0.7,
                hovertemplate='Amount: %{x}<br>Count: %{y}<extra></extra>'
            ),
            row=1, col=1
        )
        
        # Add box plot
        fig.add_trace(
            go.Box(
                y=df['total_amount'].dropna(),
                name='Amount',
                marker_color='steelblue',
                boxmean=True,
                hovertemplate='<extra></extra>'
            ),
            row=1, col=2
        )
        
        # Set title and layout
        title = "Distribution of amounts"
        if document_type:
            title += f" for {document_type} documents"
            
        fig.update_layout(
            title=title,
            showlegend=False,
            height=600,
            width=1000
        )
        
        # Update axes
        fig.update_xaxes(title_text="Amount", row=1, col=1)
        fig.update_yaxes(title_text="Frequency", row=1, col=1)
        fig.update_yaxes(title_text="Amount", row=1, col=2)
        
        # Save plot if requested
        if save:
            filename = f"interactive_amount_distribution"
            if document_type:
                filename += f"_{document_type}"
            filename += ".html"
            filepath = os.path.join(self.output_dir, filename)
            fig.write_html(filepath)
            logger.info(f"Saved interactive amount distribution plot to {filepath}")
            return filepath
        else:
            fig.show()
            return ""
    
    def create_dashboard(self, document_type: Optional[str] = None) -> List[str]:
        """
        Create a comprehensive dashboard with multiple visualizations.
        
        Args:
            document_type (str): Type of documents to include
            
        Returns:
            List[str]: Paths to saved plots
        """
        plots = []
        
        # Time series plot
        time_series_plot = self.plot_time_series(document_type=document_type)
        if time_series_plot:
            plots.append(time_series_plot)
        
        # Supplier distribution plot
        supplier_plot = self.plot_supplier_distribution(document_type=document_type)
        if supplier_plot:
            plots.append(supplier_plot)
        
        # Document type distribution plot
        if not document_type:
            doc_type_plot = self.plot_document_type_distribution()
            if doc_type_plot:
                plots.append(doc_type_plot)
        
        # Seasonal variation plot
        seasonal_plot = self.plot_seasonal_variation(document_type=document_type)
        if seasonal_plot:
            plots.append(seasonal_plot)
        
        # Amount distribution plot
        amount_plot = self.plot_amount_distribution(document_type=document_type)
        if amount_plot:
            plots.append(amount_plot)
        
        return plots
    
    def create_interactive_dashboard(self, document_type: Optional[str] = None) -> List[str]:
        """
        Create a comprehensive interactive dashboard with multiple visualizations using Plotly.
        
        Args:
            document_type (str): Type of documents to include
            
        Returns:
            List[str]: Paths to saved plots
        """
        plots = []
        
        # Interactive time series plot
        time_series_plot = self.plot_interactive_time_series(document_type=document_type)
        if time_series_plot:
            plots.append(time_series_plot)
        
        # Interactive supplier distribution plot
        supplier_plot = self.plot_interactive_supplier_distribution(document_type=document_type)
        if supplier_plot:
            plots.append(supplier_plot)
        
        # Interactive document type distribution plot
        if not document_type:
            doc_type_plot = self.plot_interactive_document_type_distribution()
            if doc_type_plot:
                plots.append(doc_type_plot)
        
        # Interactive seasonal variation plot
        seasonal_plot = self.plot_interactive_seasonal_variation(document_type=document_type)
        if seasonal_plot:
            plots.append(seasonal_plot)
        
        # Interactive amount distribution plot
        amount_plot = self.plot_interactive_amount_distribution(document_type=document_type)
        if amount_plot:
            plots.append(amount_plot)
        
        return plots
    
    def export_data_summary(self, output_file: str = "data_summary.txt") -> str:
        """
        Export a summary of the data.
        
        Args:
            output_file (str): Path to output file
            
        Returns:
            str: Path to output file
        """
        if self.df is None or self.df.empty:
            logger.warning("No data available for summary")
            return ""
        
        filepath = os.path.join(self.output_dir, output_file)
        
        try:
            with open(filepath, 'w') as f:
                # Write header
                f.write("=== DATA SUMMARY ===\n\n")
                
                # Document counts
                f.write("Document Counts:\n")
                f.write(f"Total documents: {len(self.df)}\n")
                
                # Document types
                if 'document_type' in self.df.columns:
                    doc_types = self.df['document_type'].value_counts()
                    f.write("\nDocument Types:\n")
                    for doc_type, count in doc_types.items():
                        f.write(f"  {doc_type}: {count}\n")
                
                # Date range
                if 'date' in self.df.columns and not self.df['date'].isna().all():
                    min_date = self.df['date'].min()
                    max_date = self.df['date'].max()
                    f.write(f"\nDate Range: {min_date.strftime('%Y-%m-%d')} to {max_date.strftime('%Y-%m-%d')}\n")
                
                # Amount statistics
                if 'total_amount' in self.df.columns and not self.df['total_amount'].isna().all():
                    f.write("\nAmount Statistics:\n")
                    f.write(f"  Total: {self.df['total_amount'].sum():,.2f}\n")
                    f.write(f"  Average: {self.df['total_amount'].mean():,.2f}\n")
                    f.write(f"  Median: {self.df['total_amount'].median():,.2f}\n")
                    f.write(f"  Min: {self.df['total_amount'].min():,.2f}\n")
                    f.write(f"  Max: {self.df['total_amount'].max():,.2f}\n")
                
                # Supplier statistics
                if 'supplier' in self.df.columns and not self.df['supplier'].isna().all():
                    suppliers = self.df['supplier'].nunique()
                    top_suppliers = self.df['supplier'].value_counts().head(5)
                    f.write(f"\nSuppliers: {suppliers}\n")
                    f.write("Top 5 Suppliers:\n")
                    for supplier, count in top_suppliers.items():
                        f.write(f"  {supplier}: {count}\n")
                
                # Monthly statistics
                if 'date' in self.df.columns and 'total_amount' in self.df.columns:
                    if not self.df['date'].isna().all() and not self.df['total_amount'].isna().all():
                        self.df['month_year'] = self.df['date'].dt.strftime('%Y-%m')
                        monthly = self.df.groupby('month_year')['total_amount'].sum().sort_index()
                        f.write("\nMonthly Totals:\n")
                        for month, amount in monthly.items():
                            f.write(f"  {month}: {amount:,.2f}\n")
            
            logger.info(f"Saved data summary to {filepath}")
            return filepath
        except Exception as e:
            logger.error(f"Error exporting data summary: {e}")
            return ""

# For testing
if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python data_visualizer.py <data_dir>")
        sys.exit(1)
    
    data_dir = sys.argv[1]
    visualizer = DataVisualizer(data_dir)
    
    # Create dashboard
    plots = visualizer.create_dashboard()
    
    # Create interactive dashboard
    interactive_plots = visualizer.create_interactive_dashboard()
    
    # Export data summary
    summary = visualizer.export_data_summary()
    
    print(f"Created {len(plots)} static plots and {len(interactive_plots)} interactive plots")
    print(f"Saved them to {visualizer.output_dir}")
    if summary:
        print(f"Exported data summary to {summary}")
                return ""
            
            # Group by supplier and sum amounts
            grouped = df.groupby('supplier')['total_amount'].sum().reset_index()
            grouped = grouped.sort_values('total_amount', ascending=False)
            value_col = 'total_amount'
            ylabel = 'Total amount'
        else:
            # Group by supplier and count documents
            grouped = df.groupby('supplier').size().reset_index(name='count')
            grouped = grouped.sort_values('count', ascending=False)
            value_col = 'count'
            ylabel = 'Number of documents'
        
        # Take top N suppliers
        grouped = grouped.head(top_n)
        
        # Create interactive horizontal bar chart with Plotly
        fig = px.bar(
            grouped,
            x=value_col,
            y='supplier',
            orientation='h',
            labels={'supplier': 'Supplier', value_col: ylabel},
            text=value_col,
            color=value_col,
            color_continuous_scale='Blues',
        )
        
        # Update layout
        title = f"Top {top_n} suppliers by {'amount' if by_amount else 'document count'}"
        if document_type:
            title += f" for {document_type} documents"
            
        fig.update_layout(
            title=title,
            xaxis_title=ylabel,
            yaxis_title='Supplier',
            yaxis={'categoryorder': 'total ascending'},
            hovermode="y unified"
        )
        
        # Format text on bars
        fig.update_traces(
            texttemplate='%{text:.2s}', 
            textposition='outside'
        )
        
        # Save plot if requested
        if save:
            filename = f"interactive_supplier_distribution_by_{'amount' if by_amount else 'count'}"
            if document_type:
                filename += f"_{document_type}"
            filename += ".html"
            filepath = os.path.join(self.output_dir, filename)
            fig.write_html(filepath)
            logger.info(f"Saved interactive supplier distribution plot to {filepath}")
            return filepath
        else:
            fig.show()
            return ""