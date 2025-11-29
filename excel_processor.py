"""
Optimized Excel processing utilities
Handles large Excel files efficiently with chunked reading and data validation
"""
import pandas as pd
import logging
from typing import List, Dict, Tuple, Optional
from io import BytesIO

logger = logging.getLogger("excel_processor")

class ExcelProcessor:
    """Process Excel files efficiently with chunked reading"""
    
    CHUNK_SIZE = 100  # Process rows in chunks of 100
    
    @staticmethod
    def read_excel_chunked(file_path: str, chunk_size: int = CHUNK_SIZE) -> pd.DataFrame:
        """
        Read Excel file efficiently
        
        Args:
            file_path: Path to Excel file
            chunk_size: Size of chunks for processing
            
        Returns:
            DataFrame with all data
        """
        try:
            # Try with openpyxl for .xlsx files
            df = pd.read_excel(file_path, engine='openpyxl')
            return df
        except Exception as e:
            logger.error(f"Error reading Excel file {file_path}: {e}")
            raise
    
    @staticmethod
    def validate_columns(df: pd.DataFrame, required_columns: List[str]) -> Tuple[bool, str]:
        """
        Validate that required columns exist in DataFrame
        
        Args:
            df: DataFrame to validate
            required_columns: List of required column names
            
        Returns:
            Tuple of (is_valid: bool, error_message: str)
        """
        missing_cols = [col for col in required_columns if col not in df.columns]
        if missing_cols:
            return False, f"Missing columns: {', '.join(missing_cols)}"
        return True, ""
    
    @staticmethod
    def prepare_personalized_rows(
        df: pd.DataFrame,
        target_column: str,
        custom_columns: List[str],
        progress_callback=None
    ) -> List[Dict]:
        """
        Prepare rows for personalized messaging
        Converts DataFrame to list of dictionaries with proper column mapping
        
        Args:
            df: DataFrame from Excel
            target_column: Column name for message target (chat_id)
            custom_columns: Additional columns to include
            progress_callback: Function to call with (current, total) progress
            
        Returns:
            List of prepared row dictionaries
        """
        rows = []
        total_rows = len(df)
        
        for idx, row in df.iterrows():
            row_dict = row.to_dict()
            
            # Get target value and convert to string to preserve formatting
            target_value = row_dict.get(target_column)
            
            # Critical: Convert to string early to prevent scientific notation loss
            if target_value is not None:
                target_str = str(target_value).strip()
            else:
                target_str = ""
            
            # Create new dict with 'target' key pointing to target_column value
            prepared_row = {
                'target': target_str,
            }
            
            # Add selected custom columns
            for col in custom_columns:
                value = row_dict.get(col)
                # Handle NaN values
                if pd.isna(value):
                    prepared_row[col] = ""
                else:
                    prepared_row[col] = str(value)
            
            rows.append(prepared_row)
            
            # Call progress callback every 10 rows
            if progress_callback and (idx + 1) % 10 == 0:
                progress_callback(idx + 1, total_rows)
        
        # Final progress callback
        if progress_callback:
            progress_callback(total_rows, total_rows)
        
        return rows
    
    @staticmethod
    def get_excel_preview(file_path: str, num_rows: int = 5) -> Dict:
        """
        Get preview of Excel file for UI display
        
        Args:
            file_path: Path to Excel file
            num_rows: Number of rows to preview
            
        Returns:
            Dictionary with columns and sample data
        """
        try:
            df = pd.read_excel(file_path)
            
            if df.empty:
                return {'error': 'File is empty'}
            
            columns = list(df.columns)
            
            # Get first row as sample
            sample_data = df.iloc[0].to_dict()
            sample_data_serialized = {}
            for key, value in sample_data.items():
                if pd.isna(value):
                    sample_data_serialized[key] = '[empty]'
                else:
                    sample_data_serialized[key] = str(value)
            
            return {
                'columns': columns,
                'sample_data': sample_data_serialized,
                'row_count': len(df)
            }
        except Exception as e:
            logger.error(f"Error previewing Excel: {e}")
            return {'error': str(e)}
