import os
import json
from datetime import datetime
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from django.conf import settings

def get_credentials():
    """Obtain credentials for Google Sheets access using service account."""
    try:
        # Check if Google Sheets integration is enabled in the database config
        from core.models import GoogleSheetsConfig
        config = GoogleSheetsConfig.objects.first()
        
        if not config or not config.enabled:
            print("Google Sheets integration is disabled in database settings")
            return None
            
        # Get the path to the credentials file
        credentials_file = os.path.join(settings.BASE_DIR, 'credentials.json')
        
        # Ensure credentials file exists
        if not os.path.exists(credentials_file):
            print(f"Credentials file not found: {credentials_file}")
            return None
        
        # Create credentials from service account file
        creds = Credentials.from_service_account_file(
            credentials_file,
            scopes=['https://www.googleapis.com/auth/spreadsheets']
        )
        
        return creds
        
    except Exception as e:
        print(f"Error loading service account credentials: {e}")
        return None

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

def update_sheet_with_answers(user, stage, sheet_id=None):
    """
    Update Google Sheet with user's answers for a specific stage.
    
    Args:
        user: Django User object
        stage: Stage number
        sheet_id: Google Sheet ID (optional, will use config if not provided)
    """
    try:
        from recruitment.models import Answer, Question
        from core.models import GoogleSheetsConfig
        from django.conf import settings
        
        # Get the Google Sheets configuration
        config = GoogleSheetsConfig.objects.first()
        if not config or not config.enabled:
            print("Google Sheets integration is not enabled in settings")
            return False
            
        # Use provided sheet_id or get from config
        if not sheet_id:
            sheet_id = config.spreadsheet_id
            
        if not sheet_id:
            print("No spreadsheet ID provided or configured")
            return False
        
        # Get user answers for this stage
        answers = Answer.objects.filter(
            user=user,
            question__stage__stage_number=stage
        ).order_by('question__order')
        
        # Format timestamp in the DD/MM/YYYY HH:MM:SS format as shown in the example
        timestamp = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        
        # Prepare data for Google Sheets following the example format
        row_data = [
            timestamp,                       # Marcaj de timp (Timestamp)
            "Îmi exprim acordul cu privire la GDPR",  # GDPR Agreement
            user.first_name,                 # Numele (First name)
            user.last_name,                  # Prenumele (Last name)
            "",                              # CNP (empty by default, will be filled if found)
            "",                              # Domiciliu (Address - empty by default, will be filled if found)
            user.phone_number,               # Număr de telefon (Phone number)
            user.email,                      # Adresa de e-mail (Email)
            f"Stage {stage}",                # Opțiunea primită (Option received - stage number)
            "",                              # Țara de reședință (Country - empty by default, will be filled if found)
        ]
        
        # Dictionary to maintain custom answer positions
        custom_positions = {}
        
        # Process each answer and update the relevant fields in row_data or add as new columns
        for answer in answers:
            question_type = answer.question.question_type
            question_text = answer.question.question_text.lower()
            
            # Check if this question has custom Google Sheets column mappings
            if answer.question.sheets_column or answer.question.sheets_answer_column:
                # Use custom column mapping (save for later insertion)
                q_col = answer.question.sheets_column or config.question_column or "C"
                a_col = answer.question.sheets_answer_column or config.answer_column or "F"
                
                # Convert column letters to indices (A=0, B=1, etc.)
                a_idx = ord(a_col.upper()) - ord('A')
                
                # Save for later (we'll handle custom positions after the standard fields)
                answer_value = answer.answer_text
                if question_type == 'dob' and answer.answer_text:
                    try:
                        date_obj = datetime.strptime(answer.answer_text, '%Y-%m-%d')
                        answer_value = date_obj.strftime('%d.%m.%Y')
                    except:
                        pass
                        
                # For file uploads, use file URL
                if question_type == 'file' and answer.file_upload:
                    if hasattr(settings, 'BASE_URL') and settings.BASE_URL:
                        answer_value = f"{settings.BASE_URL}{answer.file_upload.url}"
                    else:
                        answer_value = f"https://drive.google.com/file/d/{answer.file_upload.name}"
                        
                # Store the answer at the specified column position
                custom_positions[a_idx] = answer_value
                continue
                
            # Handle regular (non-custom position) fields
            # Update existing columns based on question content
            if 'cnp' in question_text or 'cod numeric personal' in question_text:
                row_data[4] = answer.answer_text  # Update CNP field
            elif 'adres' in question_text or 'domiciliu' in question_text:
                row_data[5] = answer.answer_text  # Update Address field
            elif 'țara' in question_text or 'tara' in question_text or 'country' in question_text:
                row_data[9] = answer.answer_text  # Update Country field
            elif question_type == 'file' and answer.file_upload:
                # For file uploads, add a link to the file as a new column
                if hasattr(settings, 'BASE_URL') and settings.BASE_URL:
                    file_url = f"{settings.BASE_URL}{answer.file_upload.url}"
                else:
                    file_url = f"https://drive.google.com/file/d/{answer.file_upload.name}"
                
                row_data.append(file_url)  # Add file URL as a new column
            else:
                # For other questions, check if they match existing columns
                # If not, add them as new columns with question:answer format
                if 'phone' in question_text or 'telefon' in question_text:
                    formatted_phone = answer.answer_text.replace('+49', '+49 ')
                    row_data[6] = formatted_phone  # Update Phone field
                elif 'email' in question_text or 'e-mail' in question_text:
                    row_data[7] = answer.answer_text  # Update Email field
                else:
                    # Add as a new column in format "Question: Answer"
                    if question_type == 'dob' and answer.answer_text:
                        try:
                            date_obj = datetime.strptime(answer.answer_text, '%Y-%m-%d')
                            formatted_date = date_obj.strftime('%d.%m.%Y')
                            row_data.append(formatted_date)
                        except:
                            row_data.append(answer.answer_text)
                    else:
                        row_data.append(answer.answer_text)
        
        # Insert custom position answers
        for col_idx, value in sorted(custom_positions.items()):
            # Expand row_data if needed to accommodate the custom position
            while len(row_data) <= col_idx:
                row_data.append("")
            
            # Set the value at the custom position
            row_data[col_idx] = value
        
        # Ensure the sheet exists first
        create_sheet_if_needed(sheet_id)
        
        # Append the row to Google Sheet
        sheet_name = f"Stage{stage}"
        result = append_row(row_data, sheet_id, f"{sheet_name}!A:Z")
        
        return result is not None
    except Exception as e:
        print(f"Error updating sheet with answers: {e}")
        return False

def create_sheet_if_needed(sheet_id=None):
    """
    Set up the Google Sheet with appropriate tabs for each stage.
    
    Args:
        sheet_id: Google Sheet ID (optional, will use config if not provided)
    """
    try:
        from core.models import GoogleSheetsConfig
        
        # Get the Google Sheets configuration
        config = GoogleSheetsConfig.objects.first()
        if not config or not config.enabled:
            print("Google Sheets integration is not enabled in settings")
            return False
        
        # Use provided sheet_id or get from config
        if not sheet_id:
            sheet_id = config.spreadsheet_id
            
        if not sheet_id:
            print("No spreadsheet ID provided or configured")
            return False
            
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
        
        # Add headers for each sheet matching the example format
        headers = {
            'Stage1': ['Marcaj de timp', 'GDPR Agreement', 'Numele', 'Prenumele', 'CNP (Cod Numeric Personal)', 'Domiciliul sau reședința', 'Număr de telefon', 'Adresa de E-mail', 'Opțiunea primită', 'Țara de reședință', 'Încărcare document'],
            'Stage2': ['Marcaj de timp', 'GDPR Agreement', 'Numele', 'Prenumele', 'CNP (Cod Numeric Personal)', 'Domiciliul sau reședința', 'Număr de telefon', 'Adresa de E-mail', 'Opțiunea primită', 'Țara de reședință', 'Încărcare document'],
            'Stage3': ['Marcaj de timp', 'GDPR Agreement', 'Numele', 'Prenumele', 'CNP (Cod Numeric Personal)', 'Domiciliul sau reședința', 'Număr de telefon', 'Adresa de E-mail', 'Opțiunea primită', 'Țara de reședință', 'Încărcare document']
        }
        
        # Calculate range for headers based on configuration
        header_range = f"1:{config.header_row_index}" if config.has_header_row else "1:1"
        
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
                    # Put headers in the configured header row
                    target_row = config.header_row_index if config.has_header_row else 1
                    sheets.values().update(
                        spreadsheetId=sheet_id,
                        range=f"{sheet_name}!A{target_row}:K{target_row}",
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

def sync_questions_to_sheets():
    """Sync all questions to Google Sheets with proper numbering and ordering"""
    try:
        # Get Google Sheets configuration from database
        from core.models import GoogleSheetsConfig
        config = GoogleSheetsConfig.objects.first()
        
        if not config or not config.enabled:
            return {"success": False, "error": "Google Sheets integration is not enabled in settings"}
        
        sheet_id = config.spreadsheet_id
        if not sheet_id:
            return {"success": False, "error": "No spreadsheet ID configured in Google Sheets settings"}
        
        sheets = get_service()
        if not sheets:
            return {"success": False, "error": "Could not initialize Google Sheets service. Check API key and credentials."}
        
        # Prepare data - Headers first
        data = [["Nr.", "Question", "Question Type", "Stage", "Required", "Google Sheets Column", "Answer Column"]]
        
        # Get all questions ordered by stage and order
        from recruitment.models import Question
        questions = Question.objects.all().order_by('stage__stage_number', 'order')
        
        # Add questions with sequential numbering
        for i, question in enumerate(questions, 1):
            # Get custom column settings if specified
            question_column = question.sheets_column or config.question_column or "C"
            answer_column = question.sheets_answer_column or config.answer_column or "F"
            
            data.append([
                i,  # Sequential number
                question.question_text,
                dict(Question.QUESTION_TYPES).get(question.question_type, question.question_type),
                f"{question.stage.stage_number}: {question.stage.stage_name}",
                "Yes" if question.is_required else "No",
                question_column,  # Custom column for question (or default)
                answer_column     # Custom column for answer (or default)
            ])
        
        # Create a Questions sheet if it doesn't exist
        try:
            spreadsheet = sheets.get(spreadsheetId=sheet_id).execute()
            existing_sheets = [sheet['properties']['title'] for sheet in spreadsheet['sheets']]
            
            if 'Questions' not in existing_sheets:
                sheets.batchUpdate(
                    spreadsheetId=sheet_id,
                    body={'requests': [{'addSheet': {'properties': {'title': 'Questions'}}}]}
                ).execute()
                print("Created 'Questions' sheet")
        except Exception as e:
            print(f"Error checking/creating Questions sheet: {e}")
            return {"success": False, "error": f"Error setting up Questions sheet: {str(e)}"}
        
        # Calculate start row based on header row configuration
        start_row = config.data_start_row if config.has_header_row else 1
        
        # Clear existing data and update with new data
        try:
            sheets.values().clear(
                spreadsheetId=sheet_id,
                range="Questions!A:G"
            ).execute()
            
            sheets.values().update(
                spreadsheetId=sheet_id,
                range="Questions!A1",
                valueInputOption="RAW",
                body={"values": data}
            ).execute()
            
            return {"success": True, "count": len(questions)}
        except Exception as e:
            print(f"Error updating Questions sheet data: {e}")
            return {"success": False, "error": f"Error updating Questions sheet: {str(e)}"}
            
    except Exception as e:
        print(f"Unexpected error in sync_questions_to_sheets: {e}")
        return {"success": False, "error": f"Unexpected error: {str(e)}"}