"""Google Sheets logging service."""

import logging
import asyncio
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor

import gspread
from google.oauth2.service_account import Credentials

logger = logging.getLogger(__name__)
executor = ThreadPoolExecutor(max_workers=2)


class SheetsLogger:
    """Google Sheets logging for video analysis requests."""
    
    SCOPES = [
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive"
    ]
    
    def __init__(self, spreadsheet_id: str, service_account_info: dict):
        """
        Initialize Google Sheets client.
        
        Args:
            spreadsheet_id: Google Sheets document ID
            service_account_info: Service account credentials dict
        """
        self.spreadsheet_id = spreadsheet_id
        self.service_account_info = service_account_info
        self._client = None
        self._sheet = None
        self._enabled = bool(spreadsheet_id and service_account_info)
        
        if not self._enabled:
            logger.warning("Google Sheets logging disabled (missing configuration)")
    
    def _get_sheet(self):
        """Get or create Sheets client (sync, runs in thread pool)."""
        if self._client is None and self._enabled:
            try:
                credentials = Credentials.from_service_account_info(
                    self.service_account_info,
                    scopes=self.SCOPES
                )
                self._client = gspread.authorize(credentials)
                spreadsheet = self._client.open_by_key(self.spreadsheet_id)
                
                # Get first sheet or create "Logs" sheet
                try:
                    self._sheet = spreadsheet.worksheet("Logs")
                except gspread.exceptions.WorksheetNotFound:
                    self._sheet = spreadsheet.sheet1
                    
                # Ensure headers exist
                headers = self._sheet.row_values(1)
                if not headers:
                    self._sheet.append_row([
                        "Дата", "Час", "User ID", "Username", 
                        "Посилання", "Назва відео", "Короткий саммарі"
                    ])
                    
            except Exception as e:
                logger.error(f"Failed to initialize Google Sheets: {e}")
                self._enabled = False
        
        return self._sheet
    
    async def log_request(
        self,
        user_id: int,
        username: str,
        video_url: str,
        video_title: str,
        summary_preview: str
    ) -> None:
        """
        Log video analysis request to Google Sheets.
        
        Args:
            user_id: Telegram user ID
            username: Telegram username or name
            video_url: YouTube video URL
            video_title: Video title
            summary_preview: First 200 chars of summary
        """
        if not self._enabled:
            return
        
        try:
            loop = asyncio.get_event_loop()
            await loop.run_in_executor(
                executor,
                self._append_row,
                user_id,
                username,
                video_url,
                video_title,
                summary_preview
            )
            logger.debug(f"Logged request for user {user_id}")
        except Exception as e:
            logger.error(f"Failed to log request: {e}")
    
    def _append_row(
        self,
        user_id: int,
        username: str,
        video_url: str,
        video_title: str,
        summary_preview: str
    ) -> None:
        """Sync method to append row (runs in thread pool)."""
        sheet = self._get_sheet()
        if not sheet:
            return
        
        now = datetime.now()
        row = [
            now.strftime("%Y-%m-%d"),
            now.strftime("%H:%M:%S"),
            str(user_id),
            username,
            video_url,
            video_title,
            summary_preview
        ]
        
        sheet.append_row(row, value_input_option="RAW")
