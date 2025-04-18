import os
import json
from datetime import datetime
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from django.conf import settings

def get_credentials():
    """Obtain and refresh credentials for Google Sheets access."""
    creds = None
    token_file = os.path.join(settings.BASE_DIR, 'token.json')
    credentials_file = os.path.join(settings.BASE_DIR, 'credentials.json')
    
    # Token file stores the user's access and refresh tokens
    if os.path.exists(token_file):
        try:
            creds = Credentials.from_authorized_user_info(
                json.loads(open(token_file).read()),
                ['https://www.googleapis.com/auth/spreadsheets']
            )
        except Exception as e:
            print(f"Error loading credentials from token file: {e}")
    
    # If there are no valid credentials, the user needs to log in
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            try:
                creds.refresh(Request())
            except Exception as e:
                print(f"Error refreshing credentials: {e}")
                # If refresh fails, we'll need to authorize again
                creds = None
        
        if not creds:
            try:
                if os.path.exists(credentials_file):
                    flow = InstalledAppFlow.from_client_secrets_file(
                        credentials_file,
                        ['https://www.googleapis.com/auth/spreadsheets']
                    )
                    # This will require the user to authorize manually
                    creds = flow.run_local_server(port=0)
                    
                    # Save the credentials for the next run
                    with open(token_file, 'w') as token:
                        token.write(creds.to_json())
                else:
                    print(f"Credentials file not found: {credentials_file}")
                    return None
            except Exception as e:
                print(f"Error during authorization flow: {e}")
                return None
    
    return creds

def get_service():
    """Get the Google Sheets service."""
    creds = get_credentials()
    if not creds:
        print("Failed to get credentials")
        return None
    
    try:
        service = build('sheets', 'v4', credentials=creds)
        return service.spreadsheets()
    except Exception as e:
        print(f"Error building Google Sheets service: {e}")
        return None

def append_row(values, sheet_id, range_name='Sheet1!A:Z'):
    """
    Append a new row to the Google Sheet.
    
    Args:
        values: List of values for the new row
        sheet_id: Google Sheet ID
        range_name: Range where to append values
    
    Returns:
        Dict: API response
    """
    if not sheet_id:
        print("No spreadsheet ID provided")
        return None
    
    try:
        sheets = get_service()
        if not sheets:
            print("Failed to get sheets service")
            return None
            
        body = {
            'values': [values]
        }
        result = sheets.values().append(
            spreadsheetId=sheet_id,
            range=range_name,
            valueInputOption='USER_ENTERED',
            insertDataOption='INSERT_ROWS',
            body=body
        ).execute()
        print(f"Successfully appended row to sheet: {range_name}")
        return result
    except HttpError as error:
        print(f"Google Sheets API error: {error}")
        return None
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return None

def update_sheet_with_answers(user, stage, sheet_id):
    """
    Update Google Sheet with user's answers for a specific stage.
    
    Args:
        user: Django User object
        stage: Stage number
        sheet_id: Google Sheet ID
    """
    if not sheet_id:
        print("No spreadsheet ID provided")
        return False
    
    try:
        from recruitment.models import Answer, Question
        
        # Get user answers for this stage
        answers = Answer.objects.filter(
            user=user,
            question__stage__stage_number=stage
        ).order_by('question__order')
        
        # Prepare data for Google Sheets
        row_data = [
            user.email,
            f"{user.first_name} {user.last_name}",
            f"Stage {stage}",
            datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        ]
        
        # Add each answer to the row
        for answer in answers:
            row_data.append(f"{answer.question.question_text}: {answer.answer_text}")
        
        # Append the row to Google Sheet
        sheet_name = f"Stage{stage}"
        result = append_row(row_data, sheet_id, f"{sheet_name}!A:Z")
        
        return result is not None
    except Exception as e:
        print(f"Error updating sheet with answers: {e}")
        return False

def create_sheet_if_needed(sheet_id):
    """
    Set up the Google Sheet with appropriate tabs for each stage.
    """
    if not sheet_id:
        print("No spreadsheet ID provided")
        return False
    
    try:
        sheets = get_service()
        if not sheets:
            print("Failed to get sheets service")
            return False
        
        # Get spreadsheet info
        try:
            spreadsheet = sheets.get(spreadsheetId=sheet_id).execute()
        except HttpError as error:
            print(f"Error accessing spreadsheet: {error}")
            if hasattr(error, 'reason') and 'not found' in str(error.reason).lower():
                print(f"The spreadsheet with ID {sheet_id} was not found.")
            return False
        
        # Check if required sheets already exist
        existing_sheets = [sheet['properties']['title'] for sheet in spreadsheet['sheets']]
        needed_sheets = ['Stage1', 'Stage2', 'Stage3']
        
        batch_update_requests = []
        
        # Add missing sheets
        for sheet_name in needed_sheets:
            if sheet_name not in existing_sheets:
                batch_update_requests.append({
                    'addSheet': {
                        'properties': {
                            'title': sheet_name
                        }
                    }
                })
        
        # Add headers for each sheet
        headers = {
            'Stage1': ['Email', 'Full Name', 'Stage', 'Timestamp', 'Responses...'],
            'Stage2': ['Email', 'Full Name', 'Stage', 'Timestamp', 'Responses...'],
            'Stage3': ['Email', 'Full Name', 'Stage', 'Timestamp', 'Responses...']
        }
        
        # Execute batch updates if any
        if batch_update_requests:
            try:
                sheets.batchUpdate(
                    spreadsheetId=sheet_id,
                    body={'requests': batch_update_requests}
                ).execute()
                print('Sheets created successfully')
            except HttpError as error:
                print(f"Error creating sheets: {error}")
                return False
        
        # Add headers to each sheet
        for sheet_name, header in headers.items():
            try:
                # Only add headers if the sheet exists or was just created
                if sheet_name in existing_sheets or sheet_name in needed_sheets:
                    sheets.values().update(
                        spreadsheetId=sheet_id,
                        range=f"{sheet_name}!A1:E1",
                        valueInputOption='USER_ENTERED',
                        body={'values': [header]}
                    ).execute()
            except HttpError as error:
                print(f"Error adding header to {sheet_name}: {error}")
                # Continue with other sheets even if one fails
        
        print('Google Sheet has been set up successfully')
        return True
    
    except HttpError as error:
        print(f'Google API error: {error}')
        return False
    except Exception as e:
        print(f'An unexpected error occurred: {e}')
        return False