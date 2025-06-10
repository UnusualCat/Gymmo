import os
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from flask import current_app

# Define the scopes needed. For Sheets and Drive:
SCOPES = ['https://www.googleapis.com/auth/spreadsheets', 'https://www.googleapis.com/auth/drive.metadata.readonly'] # Read-only for drive listing, full for sheets

def get_service_account_creds():
    # Path to your service account key file
    # This should be configured securely, e.g., via environment variable or Flask config
    # For this subtask, we assume it's in the instance folder and named 'service_account.json'
    key_path = os.path.join(current_app.instance_path, 'service_account.json')

    if not os.path.exists(key_path):
        current_app.logger.error(f"Service account key file not found at {key_path}")
        return None

    creds = service_account.Credentials.from_service_account_file(
        key_path, scopes=SCOPES)
    return creds

def get_sheets_service():
    creds = get_service_account_creds()
    if not creds:
        return None
    try:
        service = build('sheets', 'v4', credentials=creds)
        return service
    except Exception as e:
        current_app.logger.error(f"Failed to build Sheets service: {e}")
        return None

def get_drive_service():
    creds = get_service_account_creds()
    if not creds:
        return None
    try:
        service = build('drive', 'v3', credentials=creds)
        return service
    except Exception as e:
        current_app.logger.error(f"Failed to build Drive service: {e}")
        return None

def list_drive_files(page_size=10):
    drive_service = get_drive_service()
    if not drive_service:
        return []
    try:
        results = drive_service.files().list(
            pageSize=page_size,
            fields="nextPageToken, files(id, name, mimeType)",
            # Query to list only Google Sheets: "mimeType='application/vnd.google-apps.spreadsheet'"
            q="mimeType='application/vnd.google-apps.spreadsheet'"
        ).execute()
        items = results.get('files', [])
        return items
    except HttpError as error:
        current_app.logger.error(f'An error occurred listing Drive files: {error}')
        return []
    except Exception as e:
        current_app.logger.error(f"An unexpected error occurred listing Drive files: {e}")
        return []


def read_sheet_data(spreadsheet_id, range_name):
    sheets_service = get_sheets_service()
    if not sheets_service:
        return None
    try:
        sheet = sheets_service.spreadsheets()
        result = sheet.values().get(spreadsheetId=spreadsheet_id, range=range_name).execute()
        values = result.get('values', [])
        return values
    except HttpError as error:
        current_app.logger.error(f'An error occurred reading sheet data: {error}')
        return None
    except Exception as e:
        current_app.logger.error(f"An unexpected error occurred reading sheet data: {e}")
        return None

def write_sheet_data(spreadsheet_id, range_name, values_to_write):
    sheets_service = get_sheets_service()
    if not sheets_service:
        return False
    try:
        body = {
            'values': values_to_write
        }
        # How the input data should be interpreted.
        # VALUE_INPUT_OPTION_UNSPECIFIED: Defaults to USER_ENTERED.
        # USER_ENTERED: The values will be parsed as if the user typed them into the UI. Numbers will stay numbers, but strings may be converted to numbers, dates, etc. if they look like that.
        # RAW: The values will not be parsed and will be stored as-is.
        value_input_option = 'USER_ENTERED'

        result = sheets_service.spreadsheets().values().update(
            spreadsheetId=spreadsheet_id,
            range=range_name,
            valueInputOption=value_input_option,
            body=body
        ).execute()
        current_app.logger.info(f"{result.get('updatedCells')} cells updated.")
        return True
    except HttpError as error:
        current_app.logger.error(f'An error occurred writing sheet data: {error}')
        return False
    except Exception as e:
        current_app.logger.error(f"An unexpected error occurred writing sheet data: {e}")
        return False
