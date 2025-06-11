import os
import io
from typing import Optional
import pandas as pd
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload
from backend.app.core.config import settings

class GoogleDriveService:
    def __init__(self):
        self.credentials = service_account.Credentials.from_service_account_file(
            settings.GOOGLE_DRIVE_CREDENTIALS_FILE,
            scopes=['https://www.googleapis.com/auth/drive.readonly']
        )
        self.service = build('drive', 'v3', credentials=self.credentials)
    
    def download_file(self, file_id: str) -> Optional[pd.DataFrame]:
        try:
            request = self.service.files().export_media(
                fileId=file_id,
                mimeType='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            )
            fh = io.BytesIO()
            downloader = MediaIoBaseDownload(fh, request)
            done = False
            while done is False:
                status, done = downloader.next_chunk()
            
            fh.seek(0)
            df = pd.read_excel(fh, sheet_name="Programmi", header=None)
            return df
        except Exception as e:
            print(f"Error downloading file: {e}")
            return None
    
    def list_files(self, folder_id: Optional[str] = None) -> list:
        try:
            query = "mimeType='application/vnd.google-apps.spreadsheet'"
            if folder_id:
                query += f" and '{folder_id}' in parents"
            
            results = self.service.files().list(
                q=query,
                pageSize=100,
                fields="nextPageToken, files(id, name)"
            ).execute()
            
            return results.get('files', [])
        except Exception as e:
            print(f"Error listing files: {e}")
            return []

drive_service = GoogleDriveService() 