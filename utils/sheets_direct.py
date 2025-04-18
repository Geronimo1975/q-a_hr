"""
Direct Google Sheets integration using API key authentication.
This module provides a simpler alternative to the OAuth-based integration.
"""

import os
import requests
import json
from datetime import datetime
from django.conf import settings


def get_sheet_values(spreadsheet_id, range_name='Sheet1!A1:Z', api_key=None):
    """
    Get values from a Google Sheet using the API key authentication.
    
    Args:
        spreadsheet_id: Google Sheet ID
        range_name: Range of cells to retrieve (e.g., "Sheet1!A1:Z")
        api_key: Google API key (optional, will use settings.GOOGLE_SHEETS_API_KEY if not provided)
        
    Returns:
        Values from the sheet or None on error
    """
    if not api_key:
        api_key = getattr(settings, 'GOOGLE_SHEETS_API_KEY', None)
        
    if not api_key:
        print("No Google Sheets API key provided")
        return None
        
    url = f"https://sheets.googleapis.com/v4/spreadsheets/{spreadsheet_id}/values/{range_name}"
    params = {
        'key': api_key
    }
    
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        return response.json().get('values', [])
    except requests.exceptions.RequestException as e:
        print(f"Error fetching values from Google Sheets: {e}")
        return None


def append_values(spreadsheet_id, range_name, values, api_key=None):
    """
    Append values to a Google Sheet using the API key authentication.
    
    Args:
        spreadsheet_id: Google Sheet ID
        range_name: Range where to append (e.g., "Sheet1!A1:Z")
        values: List of values to append as a row
        api_key: Google API key (optional, will use settings.GOOGLE_SHEETS_API_KEY if not provided)
        
    Returns:
        True if successful, False otherwise
    """
    if not api_key:
        api_key = getattr(settings, 'GOOGLE_SHEETS_API_KEY', None)
        
    if not api_key:
        print("No Google Sheets API key provided")
        return False
        
    url = f"https://sheets.googleapis.com/v4/spreadsheets/{spreadsheet_id}/values/{range_name}:append"
    params = {
        'key': api_key,
        'valueInputOption': 'USER_ENTERED',
        'insertDataOption': 'INSERT_ROWS'
    }
    
    data = {
        'values': [values]
    }
    
    try:
        response = requests.post(url, params=params, json=data)
        response.raise_for_status()
        return True
    except requests.exceptions.RequestException as e:
        print(f"Error appending values to Google Sheets: {e}")
        return False


def update_sheet_with_answers(user, stage, spreadsheet_id, api_key=None):
    """
    Update Google Sheet with user's answers for a specific stage.
    
    Args:
        user: Django User object
        stage: Stage number
        spreadsheet_id: Google Sheet ID
        api_key: Google API key (optional)
        
    Returns:
        True if successful, False otherwise
    """
    if not spreadsheet_id:
        print("No spreadsheet ID provided")
        return False
    
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
                        from datetime import datetime
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
        return append_values(spreadsheet_id, f"{sheet_name}!A:Z", row_data, api_key)
        
    except Exception as e:
        print(f"Error updating sheet with answers: {e}")
        return False


def create_sheet_tabs(spreadsheet_id, api_key=None):
    """
    Ensure the Google Sheet has the necessary tabs for stages.
    Note: Creating sheets requires more permissions than read/append,
    so this might not work with just an API key.
    
    Args:
        spreadsheet_id: Google Sheet ID
        api_key: Google API key (optional)
        
    Returns:
        True if the sheets exist or were created, False otherwise
    """
    if not api_key:
        api_key = getattr(settings, 'GOOGLE_SHEETS_API_KEY', None)
        
    if not api_key:
        print("No Google Sheets API key provided")
        return False
    
    # First, get the existing sheets to check what we have
    url = f"https://sheets.googleapis.com/v4/spreadsheets/{spreadsheet_id}"
    params = {'key': api_key}
    
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        sheets = response.json().get('sheets', [])
        existing_sheet_titles = [sheet['properties']['title'] for sheet in sheets]
        
        # Check if our required sheets already exist
        needed_sheets = ['Stage1', 'Stage2', 'Stage3']
        missing_sheets = [sheet for sheet in needed_sheets if sheet not in existing_sheet_titles]
        
        if not missing_sheets:
            # All required sheets exist
            return True
            
        # We'd need to create missing sheets, but this requires more permissions
        # than just an API key typically provides. Let the user know.
        print(f"Missing sheets: {missing_sheets}")
        print("Please create these sheets manually in your Google Spreadsheet.")
        print("Headers should include: Email, Full Name, Stage, Timestamp, Responses...")
        
        return False
        
    except requests.exceptions.RequestException as e:
        print(f"Error checking Google Sheet structure: {e}")
        return False