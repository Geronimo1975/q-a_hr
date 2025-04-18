"""
Setup Google Sheets for the Delivery Driver Recruitment Platform using the direct API approach.
This script will set up the necessary tabs and headers in your Google Sheet using the API key.
"""

import os
import django
import sys
import requests
from datetime import datetime

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'driver_recruitment.settings')
django.setup()

from core.models import GoogleSheetsConfig
from django.conf import settings

# Get Google Sheets configuration
config = GoogleSheetsConfig.objects.first()
if not config or not config.enabled or not config.spreadsheet_id:
    print("Error: Google Sheets integration is not properly configured.")
    print("Please check that GoogleSheetsConfig is created with enabled=True and a valid spreadsheet_id.")
    sys.exit(1)

# Get the Google Sheets API key
api_key = os.environ.get('GOOGLE_SHEETS_API_KEY')
if not api_key:
    print("Error: GOOGLE_SHEETS_API_KEY environment variable is not set.")
    print("This key is required for direct Google Sheets API integration.")
    sys.exit(1)

# The sheet ID from the config
spreadsheet_id = config.spreadsheet_id
print(f"Using Google Spreadsheet ID: {spreadsheet_id}")

def get_sheet_info():
    """Get information about the spreadsheet."""
    url = f"https://sheets.googleapis.com/v4/spreadsheets/{spreadsheet_id}"
    params = {'key': api_key}
    
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error fetching sheet info: {e}")
        return None

def create_new_sheet(title):
    """Create a new sheet (tab) in the spreadsheet."""
    url = f"https://sheets.googleapis.com/v4/spreadsheets/{spreadsheet_id}:batchUpdate"
    params = {'key': api_key}
    
    data = {
        "requests": [
            {
                "addSheet": {
                    "properties": {
                        "title": title
                    }
                }
            }
        ]
    }
    
    try:
        response = requests.post(url, params=params, json=data)
        response.raise_for_status()
        return True
    except requests.exceptions.RequestException as e:
        print(f"Error creating sheet '{title}': {e}")
        return False

def add_headers(sheet_title):
    """Add headers to a sheet."""
    url = f"https://sheets.googleapis.com/v4/spreadsheets/{spreadsheet_id}/values/{sheet_title}!A1:N1?valueInputOption=USER_ENTERED"
    params = {'key': api_key}
    
    data = {
        "values": [
            [
                "Email",
                "Full Name",
                "Stage",
                "Timestamp",
                "Question 1",
                "Question 2",
                "Question 3",
                "Question 4",
                "Question 5", 
                "Question 6",
                "Question 7",
                "Question 8",
                "Question 9",
                "Question 10"
            ]
        ]
    }
    
    try:
        response = requests.put(url, params=params, json=data)
        response.raise_for_status()
        return True
    except requests.exceptions.RequestException as e:
        print(f"Error adding headers to '{sheet_title}': {e}")
        return False

def add_test_data(sheet_title):
    """Add test data to a sheet."""
    url = f"https://sheets.googleapis.com/v4/spreadsheets/{spreadsheet_id}/values/{sheet_title}!A2:N2:append?valueInputOption=USER_ENTERED&insertDataOption=INSERT_ROWS"
    params = {'key': api_key}
    
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    data = {
        "values": [
            [
                "test@example.com",
                "Test User",
                f"Stage {sheet_title[-1]}",
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
        ]
    }
    
    try:
        response = requests.post(url, params=params, json=data)
        response.raise_for_status()
        return True
    except requests.exceptions.RequestException as e:
        print(f"Error adding test data to '{sheet_title}': {e}")
        return False

# Main process
print("\nFetching Google Sheet information...")
sheet_info = get_sheet_info()

if not sheet_info:
    print("Failed to fetch sheet information. Check your API key and sheet ID.")
    sys.exit(1)

sheets = sheet_info.get('sheets', [])
existing_sheet_titles = [sheet['properties']['title'] for sheet in sheets]
print(f"Existing sheets: {', '.join(existing_sheet_titles)}")

# Needed sheets
needed_sheets = ['Stage1', 'Stage2', 'Stage3']
stage_sheets_created = 0
stage_headers_added = 0

# Create missing sheets and add headers
for sheet_title in needed_sheets:
    if sheet_title not in existing_sheet_titles:
        print(f"\nCreating sheet '{sheet_title}'...")
        if create_new_sheet(sheet_title):
            existing_sheet_titles.append(sheet_title)
            stage_sheets_created += 1
            print(f"✓ Created sheet '{sheet_title}'")
        else:
            print(f"✗ Failed to create sheet '{sheet_title}'")
    
    print(f"Adding headers to '{sheet_title}'...")
    if add_headers(sheet_title):
        stage_headers_added += 1
        print(f"✓ Added headers to '{sheet_title}'")
    else:
        print(f"✗ Failed to add headers to '{sheet_title}'")

# Summary
print("\n=== Setup Summary ===")
print(f"Sheets created: {stage_sheets_created} of {len(needed_sheets) - len(set(needed_sheets) & set(existing_sheet_titles))}")
print(f"Headers added: {stage_headers_added} of {len(needed_sheets)}")

# Add test data if desired
add_test = input("\nWould you like to add test data to the sheets? (y/n): ")
if add_test.lower() == 'y':
    for sheet_title in needed_sheets:
        if sheet_title in existing_sheet_titles:
            print(f"\nAdding test data to '{sheet_title}'...")
            if add_test_data(sheet_title):
                print(f"✓ Added test data to '{sheet_title}'")
            else:
                print(f"✗ Failed to add test data to '{sheet_title}'")

print("\nSetup complete. Please check your Google Sheet to verify everything is set up correctly.")