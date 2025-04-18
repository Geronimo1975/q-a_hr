"""
Script to test appending data to Google Sheets
"""
import os
import sys
import django
from datetime import datetime

# Setup Django environment
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'driver_recruitment.settings')
django.setup()

from utils.google_sheets import get_service, append_row

def test_append_data():
    """Test appending a test row to each stage sheet"""
    sheet_id = os.environ.get('GOOGLE_SHEETS_ID')
    if not sheet_id:
        print("ERROR: GOOGLE_SHEETS_ID environment variable is not set.")
        return False
    
    print(f"Testing data append for spreadsheet ID: {sheet_id}")
    
    # Test data for each stage
    test_data = {
        'Stage1': [
            'test@example.com',
            'Test User',
            'Stage 1',
            datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            'Question 1: Answer 1',
            'Question 2: Answer 2',
            'Question 3: Answer 3',
        ],
        'Stage2': [
            'test@example.com',
            'Test User',
            'Stage 2',
            datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            'Question 1: Answer 1',
            'Question 2: Answer 2',
            'Question 3: Answer 3',
        ],
        'Stage3': [
            'test@example.com',
            'Test User',
            'Stage 3',
            datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            'Question 1: Answer 1',
            'Question 2: Answer 2',
            'Question 3: Answer 3',
        ]
    }
    
    success = True
    
    # Append test data to each stage sheet
    for sheet_name, data in test_data.items():
        print(f"Appending test data to {sheet_name}...")
        try:
            result = append_row(data, sheet_id, f"{sheet_name}!A:Z")
            if result:
                print(f"SUCCESS: Data appended to {sheet_name}")
            else:
                print(f"ERROR: Failed to append data to {sheet_name}")
                success = False
        except Exception as e:
            print(f"ERROR: Exception while appending to {sheet_name}: {e}")
            success = False
    
    if success:
        print("SUCCESS: Test data appended to all sheets!")
    else:
        print("ERROR: Failed to append test data to some sheets.")
    
    return success

if __name__ == "__main__":
    test_append_data()