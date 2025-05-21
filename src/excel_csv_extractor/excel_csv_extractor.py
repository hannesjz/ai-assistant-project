"""
Excel and CSV Data Extraction Module

This module provides functionality to extract and analyze data from Excel and CSV files:
1. Excel files (.xls, .xlsx, .xlsm) using pandas and openpyxl
2. CSV files with automatic delimiter detection
3. Structured data extraction with type inference

Dependencies:
- pandas
- openpyxl
- numpy
"""

import os
import csv
import logging
import io
import chardet
from typing import Dict, List, Optional, Tuple, Union, Any
import pandas as pd
import numpy as np

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class ExcelCSVExtractor:
    """Class for extracting data from Excel and CSV files."""
    
    def __init__(self):
        """Initialize the Excel and CSV Extractor."""
        self._check_dependencies()
    
    def _check_dependencies(self) -> None:
        """Check if required dependencies are installed."""
        try:
            import pandas as pd
            logger.info(f"pandas version {pd.__version__} is installed.")
        except ImportError:
            logger.warning("pandas is not installed. This is required for Excel and CSV processing.")
            logger.warning("Install with: pip install pandas")
        
        try:
            import openpyxl
            logger.info(f"openpyxl version {openpyxl.__version__} is installed.")
        except ImportError:
            logger.warning("openpyxl is not installed. This is required for Excel processing.")
            logger.warning("Install with: pip install openpyxl")
    
    def extract_from_excel(self, file_path: str, sheet_name: Optional[Union[str, int, List]] = None) -> Dict[str, pd.DataFrame]:
        """
        Extract data from an Excel file.
        
        Args:
            file_path (str): Path to the Excel file.
            sheet_name (Optional[Union[str, int, List]]): Sheet(s) to extract. 
                                                         None for all sheets (default),
                                                         str or int for a specific sheet,
                                                         list for multiple sheets.
        
        Returns:
            Dict[str, pd.DataFrame]: Dictionary mapping sheet names to DataFrames.
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Excel file not found: {file_path}")
        
        try:
            # Read Excel file
            excel_data = pd.read_excel(file_path, sheet_name=sheet_name, engine='openpyxl')
            
            # If a single sheet was requested, convert to dict format for consistency
            if not isinstance(excel_data, dict):
                sheet_name = sheet_name if isinstance(sheet_name, (str, int)) else 0
                excel_data = {str(sheet_name): excel_data}
            
            logger.info(f"Successfully extracted data from {file_path} ({len(excel_data)} sheet(s)).")
            return excel_data
        except Exception as e:
            logger.error(f"Failed to extract data from Excel file {file_path}: {e}")
            
            # Try with xlrd engine for older .xls files
            try:
                if file_path.lower().endswith('.xls'):
                    logger.info("Trying with xlrd engine for .xls file.")
                    excel_data = pd.read_excel(file_path, sheet_name=sheet_name, engine='xlrd')
                    
                    # If a single sheet was requested, convert to dict format for consistency
                    if not isinstance(excel_data, dict):
                        sheet_name = sheet_name if isinstance(sheet_name, (str, int)) else 0
                        excel_data = {str(sheet_name): excel_data}
                    
                    logger.info(f"Successfully extracted data from {file_path} using xlrd engine.")
                    return excel_data
                else:
                    raise Exception("Not an .xls file, xlrd engine not applicable.")
            except Exception as e2:
                logger.error(f"Failed to extract data with xlrd engine: {e2}")
                return {}
    
    def extract_from_csv(self, file_path: str, delimiter: Optional[str] = None, 
                         encoding: Optional[str] = None) -> pd.DataFrame:
        """
        Extract data from a CSV file with automatic delimiter detection.
        
        Args:
            file_path (str): Path to the CSV file.
            delimiter (Optional[str]): CSV delimiter. If None, will try to detect automatically.
            encoding (Optional[str]): File encoding. If None, will try to detect automatically.
        
        Returns:
            pd.DataFrame: DataFrame containing the CSV data.
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"CSV file not found: {file_path}")
        
        try:
            # Detect encoding if not provided
            if encoding is None:
                encoding = self._detect_encoding(file_path)
            
            # Read a sample to detect delimiter if not provided
            if delimiter is None:
                delimiter = self._detect_delimiter(file_path, encoding)
            
            # Read CSV file
            df = pd.read_csv(file_path, delimiter=delimiter, encoding=encoding, 
                             on_bad_lines='warn', low_memory=False)
            
            logger.info(f"Successfully extracted data from {file_path} (delimiter: '{delimiter}', encoding: {encoding}).")
            return df
        except Exception as e:
            logger.error(f"Failed to extract data from CSV file {file_path}: {e}")
            
            # Try with a more permissive approach
            try:
                logger.info("Trying with more permissive CSV reading approach.")
                df = pd.read_csv(file_path, delimiter=delimiter, encoding=encoding, 
                                 on_bad_lines='skip', low_memory=False, 
                                 error_bad_lines=False, warn_bad_lines=True)
                
                logger.info(f"Successfully extracted data from {file_path} with permissive approach.")
                return df
            except Exception as e2:
                logger.error(f"Failed to extract data with permissive approach: {e2}")
                return pd.DataFrame()
    
    def _detect_encoding(self, file_path: str) -> str:
        """
        Detect the encoding of a file.
        
        Args:
            file_path (str): Path to the file.
        
        Returns:
            str: Detected encoding.
        """
        try:
            with open(file_path, 'rb') as f:
                result = chardet.detect(f.read(10000))
            
            encoding = result['encoding']
            confidence = result['confidence']
            
            logger.info(f"Detected encoding: {encoding} (confidence: {confidence:.2f})")
            
            # Default to utf-8 if detection failed or has low confidence
            if encoding is None or confidence < 0.7:
                logger.warning(f"Low confidence in encoding detection. Defaulting to utf-8.")
                return 'utf-8'
            
            return encoding
        except Exception as e:
            logger.error(f"Failed to detect encoding: {e}. Defaulting to utf-8.")
            return 'utf-8'
    
    def _detect_delimiter(self, file_path: str, encoding: str) -> str:
        """
        Detect the delimiter of a CSV file.
        
        Args:
            file_path (str): Path to the CSV file.
            encoding (str): File encoding.
        
        Returns:
            str: Detected delimiter.
        """
        try:
            with open(file_path, 'r', encoding=encoding, errors='replace') as f:
                sample = f.read(10000)
            
            # Use csv.Sniffer to detect the dialect
            sniffer = csv.Sniffer()
            dialect = sniffer.sniff(sample)
            delimiter = dialect.delimiter
            
            logger.info(f"Detected delimiter: '{delimiter}'")
            return delimiter
        except Exception as e:
            logger.error(f"Failed to detect delimiter: {e}. Defaulting to comma.")
            return ','
    
    def get_excel_metadata(self, file_path: str) -> Dict[str, Any]:
        """
        Extract metadata from an Excel file.
        
        Args:
            file_path (str): Path to the Excel file.
        
        Returns:
            Dict[str, Any]: Dictionary of metadata.
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Excel file not found: {file_path}")
        
        metadata = {
            'file_name': os.path.basename(file_path),
            'file_size': os.path.getsize(file_path),
            'file_extension': os.path.splitext(file_path)[1].lower(),
            'last_modified': pd.Timestamp(os.path.getmtime(file_path), unit='s').isoformat()
        }
        
        try:
            # Get sheet names
            excel_data = pd.ExcelFile(file_path)
            sheet_names = excel_data.sheet_names
            metadata['sheet_names'] = sheet_names
            metadata['sheet_count'] = len(sheet_names)
            
            # Get sheet dimensions
            sheet_dimensions = {}
            for sheet in sheet_names:
                df = pd.read_excel(file_path, sheet_name=sheet, nrows=0)
                sheet_dimensions[sheet] = {'columns': len(df.columns)}
                
                # Sample a few rows to get row count estimate
                try:
                    # Try to get exact row count for smaller files
                    df = pd.read_excel(file_path, sheet_name=sheet)
                    sheet_dimensions[sheet]['rows'] = len(df)
                except:
                    # For larger files, estimate based on file size
                    sheet_dimensions[sheet]['rows'] = 'unknown (large sheet)'
            
            metadata['sheet_dimensions'] = sheet_dimensions
            
            # Try to extract document properties if using openpyxl
            try:
                from openpyxl import load_workbook
                wb = load_workbook(filename=file_path, read_only=True)
                
                if hasattr(wb, 'properties'):
                    props = wb.properties
                    doc_props = {}
                    
                    if hasattr(props, 'creator') and props.creator:
                        doc_props['creator'] = props.creator
                    if hasattr(props, 'title') and props.title:
                        doc_props['title'] = props.title
                    if hasattr(props, 'subject') and props.subject:
                        doc_props['subject'] = props.subject
                    if hasattr(props, 'description') and props.description:
                        doc_props['description'] = props.description
                    if hasattr(props, 'keywords') and props.keywords:
                        doc_props['keywords'] = props.keywords
                    if hasattr(props, 'created') and props.created:
                        doc_props['created'] = props.created.isoformat()
                    if hasattr(props, 'modified') and props.modified:
                        doc_props['modified'] = props.modified.isoformat()
                    
                    metadata['document_properties'] = doc_props
            except Exception as e:
                logger.warning(f"Could not extract document properties: {e}")
            
            logger.info(f"Successfully extracted metadata from Excel file {file_path}.")
            return metadata
        except Exception as e:
            logger.error(f"Failed to extract metadata from Excel file {file_path}: {e}")
            return metadata
    
    def get_csv_metadata(self, file_path: str) -> Dict[str, Any]:
        """
        Extract metadata from a CSV file.
        
        Args:
            file_path (str): Path to the CSV file.
        
        Returns:
            Dict[str, Any]: Dictionary of metadata.
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"CSV file not found: {file_path}")
        
        metadata = {
            'file_name': os.path.basename(file_path),
            'file_size': os.path.getsize(file_path),
            'file_extension': os.path.splitext(file_path)[1].lower(),
            'last_modified': pd.Timestamp(os.path.getmtime(file_path), unit='s').isoformat()
        }
        
        try:
            # Detect encoding
            encoding = self._detect_encoding(file_path)
            metadata['encoding'] = encoding
            
            # Detect delimiter
            delimiter = self._detect_delimiter(file_path, encoding)
            metadata['delimiter'] = delimiter
            
            # Count lines
            with open(file_path, 'r', encoding=encoding, errors='replace') as f:
                line_count = sum(1 for _ in f)
            metadata['line_count'] = line_count
            
            # Get column names and sample data
            df = pd.read_csv(file_path, delimiter=delimiter, encoding=encoding, 
                             nrows=5, on_bad_lines='skip')
            metadata['column_count'] = len(df.columns)
            metadata['column_names'] = df.columns.tolist()
            
            # Infer column types
            column_types = {}
            for col in df.columns:
                dtype = df[col].dtype
                if pd.api.types.is_numeric_dtype(dtype):
                    if pd.api.types.is_integer_dtype(dtype):
                        column_types[col] = 'integer'
                    else:
                        column_types[col] = 'float'
                elif pd.api.types.is_datetime64_dtype(dtype):
                    column_types[col] = 'datetime'
                else:
                    # Try to detect if it's a date string
                    try:
                        pd.to_datetime(df[col], errors='raise')
                        column_types[col] = 'datetime (string)'
                    except:
                        column_types[col] = 'string'
            
            metadata['column_types'] = column_types
            
            logger.info(f"Successfully extracted metadata from CSV file {file_path}.")
            return metadata
        except Exception as e:
            logger.error(f"Failed to extract metadata from CSV file {file_path}: {e}")
            return metadata
    
    def analyze_excel_data(self, file_path: str, sheet_name: Optional[Union[str, int]] = 0) -> Dict[str, Any]:
        """
        Perform basic analysis on Excel data.
        
        Args:
            file_path (str): Path to the Excel file.
            sheet_name (Optional[Union[str, int]]): Sheet to analyze. Defaults to first sheet.
        
        Returns:
            Dict[str, Any]: Dictionary of analysis results.
        """
        try:
            # Extract data
            excel_data = self.extract_from_excel(file_path, sheet_name=sheet_name)
            
            if not excel_data:
                logger.error(f"No data extracted from {file_path}.")
                return {}
            
            # Get the sheet to analyze
            sheet_key = list(excel_data.keys())[0] if isinstance(sheet_name, (list, type(None))) else str(sheet_name)
            df = excel_data[sheet_key]
            
            # Perform analysis
            analysis = self._analyze_dataframe(df)
            analysis['sheet_name'] = sheet_key
            
            logger.info(f"Successfully analyzed data from Excel file {file_path}, sheet {sheet_key}.")
            return analysis
        except Exception as e:
            logger.error(f"Failed to analyze Excel data from {file_path}: {e}")
            return {}
    
    def analyze_csv_data(self, file_path: str, delimiter: Optional[str] = None, 
                         encoding: Optional[str] = None) -> Dict[str, Any]:
        """
        Perform basic analysis on CSV data.
        
        Args:
            file_path (str): Path to the CSV file.
            delimiter (Optional[str]): CSV delimiter. If None, will try to detect automatically.
            encoding (Optional[str]): File encoding. If None, will try to detect automatically.
        
        Returns:
            Dict[str, Any]: Dictionary of analysis results.
        """
        try:
            # Extract data
            df = self.extract_from_csv(file_path, delimiter=delimiter, encoding=encoding)
            
            if df.empty:
                logger.error(f"No data extracted from {file_path}.")
                return {}
            
            # Perform analysis
            analysis = self._analyze_dataframe(df)
            
            logger.info(f"Successfully analyzed data from CSV file {file_path}.")
            return analysis
        except Exception as e:
            logger.error(f"Failed to analyze CSV data from {file_path}: {e}")
            return {}
    
    def _analyze_dataframe(self, df: pd.DataFrame) -> Dict[str, Any]:
        """
        Perform basic analysis on a DataFrame.
        
        Args:
            df (pd.DataFrame): DataFrame to analyze.
        
        Returns:
            Dict[str, Any]: Dictionary of analysis results.
        """
        analysis = {
            'row_count': len(df),
            'column_count': len(df.columns),
            'column_names': df.columns.tolist(),
            'missing_values': df.isna().sum().to_dict(),
            'column_types': {col: str(df[col].dtype) for col in df.columns}
        }
        
        # Numeric column statistics
        numeric_stats = {}
        for col in df.select_dtypes(include=['number']).columns:
            numeric_stats[col] = {
                'min': df[col].min(),
                'max': df[col].max(),
                'mean': df[col].mean(),
                'median': df[col].median(),
                'std': df[col].std()
            }
        
        analysis['numeric_stats'] = numeric_stats
        
        # Categorical column statistics
        categorical_stats = {}
        for col in df.select_dtypes(include=['object', 'category']).columns:
            value_counts = df[col].value_counts().head(10).to_dict()  # Top 10 values
            unique_count = df[col].nunique()
            
            categorical_stats[col] = {
                'unique_count': unique_count,
                'top_values': value_counts
            }
        
        analysis['categorical_stats'] = categorical_stats
        
        # Date column detection and statistics
        date_stats = {}
        for col in df.columns:
            # Try to convert to datetime
            try:
                if df[col].dtype == 'object':
                    dates = pd.to_datetime(df[col], errors='coerce')
                    valid_dates = dates.dropna()
                    
                    # If at least 80% of values are valid dates
                    if len(valid_dates) >= 0.8 * len(df):
                        date_stats[col] = {
                            'min_date': valid_dates.min(),
                            'max_date': valid_dates.max(),
                            'range_days': (valid_dates.max() - valid_dates.min()).days,
                            'valid_count': len(valid_dates),
                            'invalid_count': len(df) - len(valid_dates)
                        }
            except:
                pass
        
        analysis['date_stats'] = date_stats
        
        # Potential monetary columns
        monetary_columns = []
        for col in df.select_dtypes(include=['number']).columns:
            # Check if column name contains monetary keywords
            col_lower = col.lower()
            if any(kw in col_lower for kw in ['amount', 'price', 'cost', 'sum', 'total', 'kr', 'sek', 'eur', 'usd']):
                monetary_columns.append(col)
            # Or if values are consistent with monetary amounts (e.g., 2 decimal places)
            elif df[col].dropna().apply(lambda x: x == round(x, 2)).mean() > 0.9:
                monetary_columns.append(col)
        
        analysis['potential_monetary_columns'] = monetary_columns
        
        return analysis
    
    def extract_structured_data(self, file_path: str, structure_type: Optional[str] = None) -> Dict[str, Any]:
        """
        Extract structured data from Excel or CSV files based on common financial document types.
        
        Args:
            file_path (str): Path to the file.
            structure_type (Optional[str]): Type of structure to extract ('invoice', 'ledger', 'balance_sheet', etc.).
                                           If None, will try to detect automatically.
        
        Returns:
            Dict[str, Any]: Extracted structured data.
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")
        
        # Determine file type
        file_ext = os.path.splitext(file_path)[1].lower()
        
        # Extract raw data
        if file_ext in ['.xlsx', '.xls', '.xlsm']:
            data = self.extract_from_excel(file_path)
            if not data:
                return {}
            
            # Use first sheet if multiple sheets
            sheet_name = list(data.keys())[0]
            df = data[sheet_name]
        elif file_ext in ['.csv', '.txt']:
            df = self.extract_from_csv(file_path)
            if df.empty:
                return {}
        else:
            logger.error(f"Unsupported file extension: {file_ext}")
            return {}
        
        # Detect structure type if not provided
        if structure_type is None:
            structure_type = self._detect_structure_type(df, file_path)
        
        # Extract structured data based on type
        if structure_type == 'invoice':
            return self._extract_invoice_data(df, file_path)
        elif structure_type == 'ledger':
            return self._extract_ledger_data(df)
        elif structure_type == 'balance_sheet':
            return self._extract_balance_sheet_data(df)
        elif structure_type == 'generic':
            return self._extract_generic_data(df)
        else:
            logger.warning(f"Unknown structure type: {structure_type}. Extracting generic data.")
            return self._extract_generic_data(df)
    
    def _detect_structure_type(self, df: pd.DataFrame, file_path: str) -> str:
        """
        Detect the structure type of a financial document.
        
        Args:
            df (pd.DataFrame): DataFrame containing the document data.
            file_path (str): Path to the file (used for filename analysis).
        
        Returns:
            str: Detected structure type.
        """
        # Check filename for clues
        filename = os.path.basename(file_path).lower()
        if any(kw in filename for kw in ['invoice', 'faktura', 'receipt', 'kvitto']):
            return 'invoice'
        elif any(kw in filename for kw in ['ledger', 'journal', 'transactions', 'transaktioner']):
            return 'ledger'
        elif any(kw in filename for kw in ['balance', 'balans', 'sheet', 'bokslut']):
            return 'balance_sheet'
        
        # Check column names for clues
        col_names = ' '.join(df.columns.astype(str).str.lower())
        if any(kw in col_names for kw in ['invoice', 'faktura', 'receipt', 'kvitto', 'amount', 'belopp']):
            return 'invoice'
        elif any(kw in col_names for kw in ['transaction', 'transaktion', 'debit', 'credit', 'kredit']):
            return 'ledger'
        elif any(kw in col_names for kw in ['asset', 'liability', 'equity', 'tillgång', 'skuld', 'eget kapital']):
            return 'balance_sheet'
        
        # Default to generic
        return 'generic'
    
    def _extract_invoice_data(self, df: pd.DataFrame, file_path: str) -> Dict[str, Any]:
        """
        Extract structured data from an invoice.
        
        Args:
            df (pd.DataFrame): DataFrame containing the invoice data.
            file_path (str): Path to the file.
        
        Returns:
            Dict[str, Any]: Extracted invoice data.
        """
        invoice_data = {
            'type': 'invoice',
            'file_path': file_path,
            'file_name': os.path.basename(file_path),
            'extracted_text': df.to_string(),
            'line_items': [],
            'metadata': {}
        }
        
        # Try to identify key invoice fields
        # This is a simplified approach - real invoices may require more sophisticated parsing
        
        # Look for invoice number
        for col in df.columns:
            col_str = str(col).lower()
            if any(kw in col_str for kw in ['invoice', 'faktura', 'number', 'nummer']):
                values = df[col].dropna().astype(str)
                if not values.empty:
                    invoice_data['metadata']['invoice_number'] = values.iloc[0]
                    break
        
        # Look for dates
        date_cols = []
        for col in df.columns:
            col_str = str(col).lower()
            if any(kw in col_str for kw in ['date', 'datum', 'day', 'dag']):
                try:
                    dates = pd.to_datetime(df[col], errors='coerce')
                    valid_dates = dates.dropna()
                    if not valid_dates.empty:
                        date_cols.append((col, valid_dates))
                except:
                    pass
        
        # Assign dates if found
        if date_cols:
            # Sort by column name to prioritize invoice date over due date
            date_cols.sort(key=lambda x: 'due' in str(x[0]).lower())
            
            # First date is likely invoice date
            invoice_data['metadata']['invoice_date'] = date_cols[0][1].iloc[0].isoformat()
            
            # If we have multiple date columns, second might be due date
            if len(date_cols) > 1:
                invoice_data['metadata']['due_date'] = date_cols[1][1].iloc[0].isoformat()
        
        # Look for total amount
        amount_cols = []
        for col in df.columns:
            col_str = str(col).lower()
            if any(kw in col_str for kw in ['total', 'amount', 'sum', 'belopp']):
                try:
                    values = pd.to_numeric(df[col], errors='coerce')
                    valid_values = values.dropna()
                    if not valid_values.empty:
                        amount_cols.append((col, valid_values))
                except:
                    pass
        
        # Assign total amount if found
        if amount_cols:
            # Sort by values to prioritize larger values (likely totals)
            amount_cols.sort(key=lambda x: x[1].max(), reverse=True)
            invoice_data['metadata']['total_amount'] = float(amount_cols[0][1].max())
        
        # Try to extract line items
        # Look for tables with item descriptions and amounts
        item_cols = {}
        for col in df.columns:
            col_str = str(col).lower()
            if any(kw in col_str for kw in ['description', 'item', 'beskrivning', 'artikel']):
                item_cols['description'] = col
            elif any(kw in col_str for kw in ['quantity', 'antal', 'qty']):
                item_cols['quantity'] = col
            elif any(kw in col_str for kw in ['price', 'pris']):
                item_cols['price'] = col
            elif any(kw in col_str for kw in ['amount', 'belopp', 'sum']):
                item_cols['amount'] = col
        
        # If we have at least description and amount, extract line items
        if 'description' in item_cols and ('amount' in item_cols or 'price' in item_cols):
            for _, row in df.iterrows():
                desc = row.get(item_cols['description'])
                if pd.isna(desc) or str(desc).strip() == '':
                    continue
                
                item = {'description': str(desc)}
                
                if 'quantity' in item_cols:
                    qty = row.get(item_cols['quantity'])
                    if not pd.isna(qty):
                        item['quantity'] = float(qty)
                
                if 'price' in item_cols:
                    price = row.get(item_cols['price'])
                    if not pd.isna(price):
                        item['price'] = float(price)
                
                if 'amount' in item_cols:
                    amount = row.get(item_cols['amount'])
                    if not pd.isna(amount):
                        item['amount'] = float(amount)
                
                invoice_data['line_items'].append(item)
        
        return invoice_data
    
    def _extract_ledger_data(self, df: pd.DataFrame) -> Dict[str, Any]:
        """
        Extract structured data from a ledger or transaction list.
        
        Args:
            df (pd.DataFrame): DataFrame containing the ledger data.
        
        Returns:
            Dict[str, Any]: Extracted ledger data.
        """
        ledger_data = {
            'type': 'ledger',
            'transactions': [],
            'metadata': {
                'row_count': len(df),
                'column_count': len(df.columns)
            }
        }
        
        # Try to identify key transaction fields
        date_col = None
        description_col = None
        amount_col = None
        debit_col = None
        credit_col = None
        account_col = None
        
        # Identify columns
        for col in df.columns:
            col_str = str(col).lower()
            
            # Date column
            if date_col is None and any(kw in col_str for kw in ['date', 'datum', 'day', 'dag']):
                try:
                    dates = pd.to_datetime(df[col], errors='coerce')
                    if dates.notna().sum() > len(df) * 0.5:  # At least 50% valid dates
                        date_col = col
                except:
                    pass
            
            # Description column
            if description_col is None and any(kw in col_str for kw in ['description', 'text', 'beskrivning', 'memo']):
                description_col = col
            
            # Amount column (single column for amount)
            if amount_col is None and any(kw in