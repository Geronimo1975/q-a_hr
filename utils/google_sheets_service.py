"""
Google Sheets integration using Service Account authentication.
This module provides direct access to Google Sheets using a service account.
"""

import os
from google.oauth2 import service_account
from googleapiclient.discovery import build
from datetime import datetime
from django.conf import settings
from google.oauth2.service_account import Credentials
import json

SCOPES = ['https://www.googleapis.com/auth/spreadsheets']

def get_credentials():
    """Get Google API credentials from the service account file."""
    try:
        creds = None
        credentials_path = os.path.join(settings.BASE_DIR, 'credentials.json')
        
        if os.path.exists(credentials_path):
            creds = service_account.Credentials.from_service_account_file(
                credentials_path, scopes=SCOPES)
        return creds
    except Exception as e:
        print(f"Error getting credentials: {e}")
        return None

def get_sheet_service():
    """Get Google Sheets API service."""
    try:
        creds = get_credentials()
        if not creds:
            return None
        
        service = build('sheets', 'v4', credentials=creds)
        return service
    except Exception as e:
        print(f"Error building sheet service: {e}")
        return None

def get_sheet_values(spreadsheet_id, range_name):
    """
    Get values from a Google Sheet using service account authentication.
    
    Args:
        spreadsheet_id: Google Sheet ID
        range_name: Range of cells to retrieve (e.g., "Sheet1!A1:Z")
        
    Returns:
        Values from the sheet or None on error
    """
    try:
        service = get_sheet_service()
        if not service:
            return None
        
        result = service.spreadsheets().values().get(
            spreadsheetId=spreadsheet_id,
            range=range_name
        ).execute()
        
        return result.get('values', [])
    except Exception as e:
        print(f"Error getting sheet values: {e}")
        return None

def append_values(spreadsheet_id, range_name, values):
    """
    Append values to a Google Sheet using service account authentication.
    
    Args:
        spreadsheet_id: Google Sheet ID
        range_name: Range where to append (e.g., "Sheet1!A1:Z")
        values: List of values to append as a row
        
    Returns:
        True if successful, False otherwise
    """
    try:
        service = get_sheet_service()
        if not service:
            return False
        
        value_range_body = {
            "values": [values]
        }
        
        result = service.spreadsheets().values().append(
            spreadsheetId=spreadsheet_id,
            range=range_name,
            valueInputOption="USER_ENTERED",
            insertDataOption="INSERT_ROWS",
            body=value_range_body
        ).execute()
        
        return True
    except Exception as e:
        print(f"Error appending values: {e}")
        return False

def create_sheet_tabs(spreadsheet_id):
    """
    Create the necessary tabs (sheets) in the Google Sheet for each recruitment stage.
    
    Args:
        spreadsheet_id: Google Sheet ID
        
    Returns:
        True if successful, False otherwise
    """
    try:
        service = get_sheet_service()
        if not service:
            return False
        
        # First, get the existing sheets to check what we have
        spreadsheet = service.spreadsheets().get(
            spreadsheetId=spreadsheet_id
        ).execute()
        
        sheets = spreadsheet.get('sheets', [])
        existing_sheet_titles = [sheet['properties']['title'] for sheet in sheets]
        
        # Check if our required sheets already exist
        needed_sheets = ['Stage1', 'Stage2', 'Stage3']
        missing_sheets = [sheet for sheet in needed_sheets if sheet not in existing_sheet_titles]
        
        if not missing_sheets:
            # All required sheets exist
            print("All required sheets already exist in the Google Sheet.")
            return True
        
        # Create the missing sheets
        requests = []
        for sheet_title in missing_sheets:
            requests.append({
                'addSheet': {
                    'properties': {
                        'title': sheet_title
                    }
                }
            })
        
        if requests:
            body = {'requests': requests}
            service.spreadsheets().batchUpdate(
                spreadsheetId=spreadsheet_id,
                body=body
            ).execute()
            print(f"Created sheets: {missing_sheets}")
        
        # Now add headers to each sheet
        for sheet_title in needed_sheets:
            # Check if the sheet already has headers
            range_name = f"{sheet_title}!A1:Z1"
            values = get_sheet_values(spreadsheet_id, range_name)
            
            if not values or len(values) == 0:
                # Add headers
                headers = [
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
                
                value_range_body = {
                    "values": [headers]
                }
                
                service.spreadsheets().values().update(
                    spreadsheetId=spreadsheet_id,
                    range=range_name,
                    valueInputOption="USER_ENTERED",
                    body=value_range_body
                ).execute()
                
                print(f"Added headers to sheet: {sheet_title}")
        
        return True
        
    except Exception as e:
        print(f"Error creating sheet tabs: {e}")
        return False

def update_sheet_with_answers(user, stage, spreadsheet_id):
    """
    Update Google Sheet with user's answers for a specific stage.
    
    Args:
        user: Django User object
        stage: Stage number
        spreadsheet_id: Google Sheet ID
        
    Returns:
        True if successful, False otherwise
    """
    try:
        from recruitment.models import Answer, Question
        
        # Get user answers for this stage
        answers = Answer.objects.filter(
            user=user,
            question__stage__stage_number=stage
        ).order_by('question__order')
        
        if not answers:
            print(f"No answers found for user {user.email}, stage {stage}")
            return False
        
        # Prepare data for Google Sheets
        row_data = [
            user.email,
            f"{user.first_name} {user.last_name}",
            f"Stage {stage}",
            datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        ]
        
        # Create a dictionary to store answers by question order
        answer_by_order = {}
        for answer in answers:
            answer_by_order[answer.question.order] = answer
        
        # Add each answer to the row, ensuring all 10 questions are represented
        for order in range(1, 11):
            if order in answer_by_order:
                answer = answer_by_order[order]
                question_type = answer.question.question_type
                
                if question_type == 'file' and answer.file_upload:
                    # For file uploads, include a note
                    row_data.append(f"File uploaded: {answer.file_upload.name}")
                elif question_type == 'dob' and answer.answer_text:
                    # Format date of birth in German format (DD.MM.YYYY)
                    try:
                        date_obj = datetime.strptime(answer.answer_text, '%Y-%m-%d')
                        formatted_date = date_obj.strftime('%d.%m.%Y')
                        row_data.append(formatted_date)
                    except:
                        row_data.append(answer.answer_text)
                elif question_type == 'phone' and answer.answer_text:
                    # Format phone number for better readability
                    formatted_phone = answer.answer_text.replace('+49', '+49 ')
                    row_data.append(formatted_phone)
                else:
                    # Standard formatting for other question types
                    row_data.append(answer.answer_text)
            else:
                # No answer for this question order
                row_data.append("")
        
        # Append the row to Google Sheet
        sheet_name = f"Stage{stage}"
        return append_values(spreadsheet_id, f"{sheet_name}!A:Z", row_data)
        
    except Exception as e:
        print(f"Error updating sheet with answers: {e}")
        return False