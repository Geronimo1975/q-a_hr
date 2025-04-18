import os
import django
import json

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'driver_recruitment.settings')
django.setup()

from utils.google_sheets import create_sheet_if_needed, append_row
from core.models import GoogleSheetsConfig

# Get Google Sheets configuration
config = GoogleSheetsConfig.objects.first()
if not config or not config.enabled or not config.spreadsheet_id:
    print("Error: Google Sheets integration is not properly configured.")
    print("Please check that GoogleSheetsConfig is created with enabled=True and a valid spreadsheet_id.")
    exit(1)

# Check for credentials.json
if not os.path.exists('credentials.json'):
    print("Error: credentials.json file not found.")
    print("This file is required for Google Sheets API authentication.")
    
    # Check if there's an example file
    if os.path.exists('credentials.json.example'):
        print("Found credentials.json.example. Checking its content...")
        with open('credentials.json.example', 'r') as f:
            example_content = f.read()
        print(f"Example content: {example_content}")
        
        print("Creating a credentials.json file for testing purposes...")
        try:
            # Create credentials.json based on the example
            with open('credentials.json', 'w') as f:
                # Use a placeholder or create proper credentials
                dummy_credentials = {
                    "web": {
                        "client_id": "your-client-id.apps.googleusercontent.com",
                        "project_id": "your-project-id",
                        "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                        "token_uri": "https://oauth2.googleapis.com/token",
                        "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
                        "client_secret": "your-client-secret",
                        "redirect_uris": ["http://localhost"]
                    }
                }
                f.write(json.dumps(dummy_credentials, indent=2))
            print("Test credentials.json file created. Please replace with actual Google API credentials.")
        except Exception as e:
            print(f"Failed to create credentials.json: {e}")
    
    print("\nTo use Google Sheets integration, you need to:")
    print("1. Create a Google Cloud Platform project")
    print("2. Enable the Google Sheets API")
    print("3. Create OAuth 2.0 credentials")
    print("4. Download the credentials as credentials.json")
    print("5. Place the credentials.json file in the project root directory")
    exit(1)

# Test sheet creation
print(f"\nTesting Google Sheets integration with sheet ID: {config.spreadsheet_id}")
success = create_sheet_if_needed(config.spreadsheet_id)

if success:
    print("Successfully set up Google Sheets with the required tabs.")
    
    # Test adding a row of test data
    print("\nAdding test data to Stage1 tab...")
    test_data = [
        "test@example.com",
        "Test User",
        "Stage 1",
        "2025-04-18 15:30:00",
        "Question 1: Text answer",
        "Question 2: 42",
        "Question 3: Yes",
        "Question 4: Option A"
    ]
    
    result = append_row(test_data, config.spreadsheet_id, "Stage1!A:Z")
    if result:
        print("Successfully added test data!")
    else:
        print("Failed to add test data.")
else:
    print("Failed to set up Google Sheets. See error messages above.")