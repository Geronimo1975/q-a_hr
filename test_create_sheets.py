"""
Script to test the creation of Google Sheets tabs for stages
"""
import os
import sys
import django

# Setup Django environment
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'driver_recruitment.settings')
django.setup()

from utils.google_sheets import create_sheet_if_needed

def test_create_sheets():
    """Test creating the required sheets in Google Spreadsheet"""
    sheet_id = os.environ.get('GOOGLE_SHEETS_ID')
    if not sheet_id:
        print("ERROR: GOOGLE_SHEETS_ID environment variable is not set.")
        return False
    
    print(f"Testing sheet creation for ID: {sheet_id}")
    result = create_sheet_if_needed(sheet_id)
    
    if result:
        print("SUCCESS: All sheets created successfully!")
    else:
        print("ERROR: Failed to create sheets.")
    
    return result

if __name__ == "__main__":
    test_create_sheets()