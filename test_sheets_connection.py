"""
Test script for Google Sheets connection
"""

import os
import sys
import json
from pathlib import Path

# Add the project directory to the path so we can import from utils
BASE_DIR = Path(__file__).resolve().parent
sys.path.append(str(BASE_DIR))

# Set Django settings module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'driver_recruitment.settings')

try:
    import django
    django.setup()
    from utils.google_sheets import get_service, sync_questions_to_sheets
    using_django = True
except Exception as e:
    print(f"Error importing Django: {e}")
    using_django = False

def test_env_variables():
    """Test if the required environment variables are set"""
    sheets_enabled = os.environ.get('GOOGLE_SHEETS_ENABLED')
    sheets_id = os.environ.get('GOOGLE_SHEETS_ID')
    
    print("Environment Variables:")
    print(f"GOOGLE_SHEETS_ENABLED: {sheets_enabled}")
    print(f"GOOGLE_SHEETS_ID: {sheets_id}")
    
    if not sheets_enabled or sheets_enabled.lower() != 'true':
        print("WARNING: Google Sheets integration is disabled (GOOGLE_SHEETS_ENABLED != True)")
        return False
        
    if not sheets_id:
        print("ERROR: Google Sheets ID is not set (GOOGLE_SHEETS_ID)")
        return False
    
    return True

def test_credentials():
    """Test if the credentials file exists and is valid"""
    creds_path = os.path.join(BASE_DIR, 'credentials.json')
    
    if not os.path.exists(creds_path):
        print(f"ERROR: credentials.json file not found at {creds_path}")
        return False
    
    print(f"Found credentials at: {creds_path}")
    
    # Verify the file is valid JSON
    try:
        with open(creds_path, 'r') as f:
            creds_data = json.load(f)
        
        # Check if it contains required fields
        if 'client_email' not in creds_data:
            print("ERROR: credentials.json is missing 'client_email' field")
            return False
        
        print(f"Service account email: {creds_data.get('client_email')}")
        print("Credentials file is valid JSON")
        return True
    except json.JSONDecodeError:
        print("ERROR: credentials.json is not valid JSON")
        return False
    except Exception as e:
        print(f"ERROR reading credentials file: {str(e)}")
        return False

def test_google_api():
    """Test connection to Google Sheets API"""
    try:
        from google.oauth2.service_account import Credentials
        from googleapiclient.discovery import build
        
        creds_path = os.path.join(BASE_DIR, 'credentials.json')
        if not os.path.exists(creds_path):
            print("ERROR: credentials.json file not found")
            return False
        
        # Load credentials
        creds = Credentials.from_service_account_file(
            creds_path,
            scopes=['https://www.googleapis.com/auth/spreadsheets']
        )
        
        # Build API service
        service = build('sheets', 'v4', credentials=creds)
        sheets = service.spreadsheets()
        
        # Get spreadsheet ID from environment
        sheets_id = os.environ.get('GOOGLE_SHEETS_ID')
        
        # Try to get spreadsheet info
        response = sheets.get(spreadsheetId=sheets_id).execute()
        
        print("\nSpreadsheet Information:")
        print(f"Title: {response.get('properties', {}).get('title')}")
        print("Sheets:")
        for sheet in response.get('sheets', []):
            print(f"  - {sheet.get('properties', {}).get('title')}")
        
        # Test if we can write to the spreadsheet
        import datetime
        test_data = [["Test connection", str(datetime.datetime.now())]]
        
        try:
            # Try to update Sheet1!A1
            result = sheets.values().update(
                spreadsheetId=sheets_id,
                range="Sheet1!A1:B1",
                valueInputOption="RAW",
                body={"values": test_data}
            ).execute()
            
            print("\nTest write successful!")
            print(f"Updated {result.get('updatedCells')} cells")
        except Exception as e:
            print(f"\nERROR writing to Sheet1: {str(e)}")
            print("Trying to create a test sheet...")
            
            # Try to create a new sheet
            try:
                request = {
                    'addSheet': {
                        'properties': {
                            'title': 'TestSheet'
                        }
                    }
                }
                
                sheets.batchUpdate(
                    spreadsheetId=sheets_id,
                    body={'requests': [request]}
                ).execute()
                
                # Try writing to the new sheet
                result = sheets.values().update(
                    spreadsheetId=sheets_id,
                    range="TestSheet!A1:B1",
                    valueInputOption="RAW",
                    body={"values": test_data}
                ).execute()
                
                print("Created TestSheet and wrote test data successfully!")
            except Exception as e2:
                print(f"ERROR creating test sheet: {str(e2)}")
                print("\nPossible causes:")
                print("- The service account doesn't have edit access to the spreadsheet")
                print(f"- Make sure to share the spreadsheet with: {Credentials.from_service_account_file(creds_path).service_account_email}")
                return False
        
        return True
        
    except Exception as e:
        print(f"\nERROR connecting to Google Sheets API: {str(e)}")
        return False

def test_django_integration():
    """Test Django integration with Google Sheets"""
    if not using_django:
        print("Django not set up, skipping test_django_integration")
        return False
    
    print("\nTesting Django integration with Google Sheets...")
    
    # Test get_service function
    sheets = get_service()
    if not sheets:
        print("ERROR: get_service() returned None")
        return False
    
    print("get_service() returned successfully")
    
    # Test sync_questions_to_sheets function
    try:
        sync_result = sync_questions_to_sheets()
        print(f"sync_questions_to_sheets result: {sync_result}")
        if sync_result.get('success'):
            print(f"Successfully synced {sync_result.get('count')} questions to Google Sheets")
            return True
        else:
            print(f"Error syncing questions: {sync_result.get('error')}")
            return False
    except Exception as e:
        print(f"ERROR in sync_questions_to_sheets: {str(e)}")
        return False

def run_all_tests():
    """Run all connection tests"""
    print("=" * 50)
    print("GOOGLE SHEETS CONNECTION TESTER")
    print("=" * 50)
    
    # Check environment variables
    print("\n[1/4] Checking environment variables...")
    env_ok = test_env_variables()
    
    # Check credentials file
    print("\n[2/4] Checking credentials file...")
    creds_ok = test_credentials()
    
    # Test Google API connection
    print("\n[3/4] Testing Google Sheets API connection...")
    api_ok = test_google_api()
    
    # Test Django integration
    django_ok = True
    if using_django:
        print("\n[4/4] Testing Django integration...")
        django_ok = test_django_integration()
    else:
        print("\n[4/4] Skipping Django integration test (Django not set up)")
    
    # Print summary
    print("\n" + "=" * 50)
    print("TEST RESULTS SUMMARY")
    print("=" * 50)
    print(f"Environment Variables: {'✓ OK' if env_ok else '✗ FAILED'}")
    print(f"Credentials File: {'✓ OK' if creds_ok else '✗ FAILED'}")
    print(f"Google Sheets API: {'✓ OK' if api_ok else '✗ FAILED'}")
    if using_django:
        print(f"Django Integration: {'✓ OK' if django_ok else '✗ FAILED'}")
    
    if env_ok and creds_ok and api_ok and (not using_django or django_ok):
        print("\n✅ ALL TESTS PASSED - Google Sheets integration is working correctly!")
    else:
        print("\n❌ SOME TESTS FAILED - Please check the errors above")

if __name__ == "__main__":
    run_all_tests()