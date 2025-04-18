import os
import django
import sys

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'driver_recruitment.settings')
django.setup()

from core.models import GoogleSheetsConfig
from utils.sheets_direct import create_sheet_tabs, append_values, get_sheet_values
from datetime import datetime
from django.conf import settings

# Get Google Sheets configuration
config = GoogleSheetsConfig.objects.first()
if not config or not config.enabled or not config.spreadsheet_id:
    print("Error: Google Sheets integration is not properly configured.")
    print("Please check that GoogleSheetsConfig is created with enabled=True and a valid spreadsheet_id.")
    sys.exit(1)

# Check for API key
google_sheets_api_key = os.environ.get('GOOGLE_SHEETS_API_KEY')
if not google_sheets_api_key:
    print("Error: GOOGLE_SHEETS_API_KEY environment variable is not set.")
    print("This key is required for direct Google Sheets API integration.")
    print("\nTo use Google Sheets integration with API key, you need to:")
    print("1. Create a Google Cloud Platform project")
    print("2. Enable the Google Sheets API")
    print("3. Create an API key")
    print("4. Set the GOOGLE_SHEETS_API_KEY environment variable")
    print("\nWould you like to provide this now? (y/n)")
    response = input()
    if response.lower() == 'y':
        google_sheets_api_key = input("Please enter your Google Sheets API key: ").strip()
        if not google_sheets_api_key:
            print("No API key provided. Exiting.")
            sys.exit(1)
    else:
        print("Exiting.")
        sys.exit(1)

# The sheet ID from the config
spreadsheet_id = config.spreadsheet_id
print(f"Using Google Spreadsheet ID: {spreadsheet_id}")

# Try to ensure we have the required sheets
print("\nChecking if the spreadsheet has the necessary tabs...")
tabs_exist = create_sheet_tabs(spreadsheet_id, google_sheets_api_key)
if not tabs_exist:
    print("Please make sure your Google Sheet has tabs named: Stage1, Stage2, Stage3")
    print("Each tab should have headers: Email, Full Name, Stage, Timestamp, Responses...")

# Try to get values from the spreadsheet
print("\nTrying to read values from the spreadsheet...")
values = get_sheet_values(spreadsheet_id, 'Sheet1!A1:Z', google_sheets_api_key)
if values:
    print(f"Successfully read {len(values)} row(s) from the spreadsheet.")
    if len(values) > 0:
        print(f"First row: {values[0]}")
else:
    print("Could not read values from the spreadsheet.")
    print("This could be due to permissions or API key issues.")

# Try to append a test row
print("\nTrying to append a test row to the spreadsheet...")
current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
test_row = [
    "test@example.com",
    "Test User",
    "Sample Stage",
    current_time,
    "This is a test row added by the application to verify Google Sheets integration."
]

success = append_values(spreadsheet_id, 'Stage1!A:Z', test_row, google_sheets_api_key)
if success:
    print("Successfully added test row to the spreadsheet!")
    print("Please check your Google Sheet to verify the test data was added correctly.")
else:
    print("Failed to add test row to the spreadsheet.")
    print("This could be due to permissions or API key issues.")

print("\nTest completed.")