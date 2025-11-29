#!/usr/bin/env python3
"""
Fix Excel chat_id column formatting - convert scientific notation to text
IMPORTANT: This tool is for data that's ALREADY corrupted by Excel.
For best results, manually format the column as TEXT in Excel BEFORE saving.
"""

import sys
import pandas as pd
from pathlib import Path

def fix_excel_chat_ids(input_file, output_file=None):
    """
    Fix Excel file by converting chat_id column to text format.
    NOTE: This is a lossy fix - data corrupted by Excel can't be fully recovered.
    
    BEST PRACTICE - Format as Text in Excel:
    1. Open the Excel file
    2. Select the chat_id/phone column
    3. Right-click → Format Cells
    4. Select "Text" category
    5. Save the file
    
    This prevents Excel from converting large numbers to scientific notation.
    """
    
    if output_file is None:
        output_file = input_file.replace('.xlsx', '_fixed.xlsx').replace('.xls', '_fixed.xlsx')
    
    print("\n" + "="*70)
    print("EXCEL FORMATTING FIX UTILITY")
    print("="*70)
    print("\nWARNING: This fixes already-corrupted data (data loss may occur)")
    print("BEST PRACTICE: Format column as TEXT before saving in Excel\n")
    
    print(f"Reading: {input_file}")
    
    # Read Excel file as strings to preserve formatting
    try:
        df = pd.read_excel(input_file, dtype=str)
    except:
        df = pd.read_excel(input_file)
    
    print(f"\nOriginal data (first 10 rows):")
    print(df.head(10))
    
    # Identify numeric columns (chat_id, phone, target, etc)
    numeric_cols = []
    for col in df.columns:
        col_lower = col.lower()
        if any(x in col_lower for x in ['chat_id', 'phone', 'target', 'id']):
            numeric_cols.append(col)
    
    if numeric_cols:
        print(f"\nDetected numeric columns: {numeric_cols}")
        print("Attempting to recover from scientific notation...\n")
        
        for col in numeric_cols:
            if col in df.columns:
                original_count = len(df)
                
                # Convert scientific notation back to regular numbers
                def parse_number(x):
                    if pd.isna(x):
                        return ""
                    x_str = str(x).strip()
                    if not x_str:
                        return ""
                    try:
                        # Handle scientific notation
                        if 'E' in x_str.upper():
                            # Convert float to int, then back to string
                            num = int(float(x_str))
                            return str(num)
                        else:
                            # Try to parse as integer
                            return str(int(float(x_str)))
                    except:
                        # Keep as-is if not a number
                        return x_str
                
                df[col] = df[col].apply(parse_number)
                print(f"  ✅ Fixed column: {col}")
    
    print(f"\nFixed data (first 10 rows):")
    print(df.head(10))
    
    # Write with proper formatting
    print(f"\nSaving with text formatting...")
    with pd.ExcelWriter(output_file, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Users')
        
        # Format numeric columns as text to prevent future corruption
        workbook = writer.book
        worksheet = writer.sheets['Users']
        
        for row in worksheet.iter_rows(min_col=1, max_col=len(df.columns)):
            for cell in row:
                col_header = worksheet.cell(1, cell.column).value
                if col_header in numeric_cols:
                    cell.number_format = '@'  # Text format code
    
    print(f"✅ Saved fixed file: {output_file}")
    print(f"   Total rows: {len(df)}")
    
    print("\n" + "="*70)
    print("BEST PRACTICES FOR FUTURE EXCEL FILES")
    print("="*70)
    print("""
1. CREATE THE FILE CORRECTLY:
   - Open Excel
   - Before entering data, format the column as TEXT
   - Right-click column → Format Cells → Text
   - Then enter your chat IDs/phone numbers

2. OR USE GOOGLE SHEETS:
   - Google Sheets preserves numbers better
   - Export as .csv instead of .xlsx

3. OR USE THE CONVERSION TOOL:
   - Save as .csv from Excel
   - Use this tool to convert back to proper .xlsx

4. VERIFY YOUR DATA:
   - Check that numbers aren't in scientific notation
   - Large IDs should show as: 201285177841 (not 2.01285E+11)
""")
    print("="*70 + "\n")
    
    return output_file


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python fix_excel_formatting.py <input_file> [output_file]")
        print("\nExample: python fix_excel_formatting.py users.xlsx users_fixed.xlsx")
        sys.exit(1)
    
    input_file = sys.argv[1]
    output_file = sys.argv[2] if len(sys.argv) > 2 else None
    
    if not Path(input_file).exists():
        print(f"Error: File not found: {input_file}")
        sys.exit(1)
    
    fix_excel_chat_ids(input_file, output_file)
