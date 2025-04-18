"""
Setup Google Sheets for the Delivery Driver Recruitment Platform.
This script will create the necessary tabs and add headers to your Google Sheet.
"""

import os
import django
import sys

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'driver_recruitment.settings')
django.setup()

from core.models import GoogleSheetsConfig
from utils.google_sheets_service import create_sheet_tabs, append_values, get_sheet_values

# Get Google Sheets configuration
config = GoogleSheetsConfig.objects.first()
if not config or not config.enabled or not config.spreadsheet_id:
    print("Error: Google Sheets integration is not properly configured.")
    print("Please check that GoogleSheetsConfig is created with enabled=True and a valid spreadsheet_id.")
    sys.exit(1)

# Check for credentials.json
if not os.path.exists('credentials.json'):
    print("Error: credentials.json file not found.")
    print("This file is required for Google Sheets API authentication.")
    sys.exit(1)

# The sheet ID from the config
spreadsheet_id = config.spreadsheet_id
print(f"Using Google Spreadsheet ID: {spreadsheet_id}")

# Create the necessary tabs
print("\nSetting up sheet tabs with stage headers...")
success = create_sheet_tabs(spreadsheet_id)

if success:
    print("✓ Successfully set up Google Sheets with the required tabs and headers!")
    
    # Add test data if desired
    add_test_data = input("\nWould you like to add some test data? (y/n): ")
    if add_test_data.lower() == 'y':
        print("\nAdding test data to Stage1 tab...")
        
        from datetime import datetime
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        test_data = [
            "test@example.com",
            "Test User",
            "Stage 1",
            current_time,
            "What is your name? John Smith",
            "How old are you? 28",
            "Do you have a driving license? Yes",
            "What kind of vehicle do you have? Compact Car",
            "How many years of driving experience do you have? 7",
            "Are you available for weekend shifts? Yes",
            "Do you have a smartphone? Yes",
            "Are you familiar with Google Maps? Yes",
            "Do you have previous delivery experience? No",
            "Can you carry packages up to 20kg? Yes"
        ]
        
        result = append_values(spreadsheet_id, "Stage1!A:Z", test_data)
        if result:
            print("✓ Successfully added test data!")
        else:
            print("✗ Failed to add test data.")
else:
    print("✗ Failed to set up Google Sheets. Check the error messages above.")

print("\nSetup complete. Please check your Google Sheet to verify everything is set up correctly.")