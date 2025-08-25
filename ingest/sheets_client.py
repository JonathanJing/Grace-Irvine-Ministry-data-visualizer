from __future__ import annotations

from typing import List
from pathlib import Path

import yaml
from google.auth import default
from google.oauth2 import service_account
from googleapiclient.discovery import build


# Scopes for Google Sheets read access
SCOPES = ["https://www.googleapis.com/auth/spreadsheets.readonly"]


def load_config() -> dict:
    with open("configs/config.yaml", "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def get_credentials():
    """Get credentials using Application Default Credentials (for Cloud Run) or service account file (for local dev)."""
    service_account_path = Path("configs/service_account.json")
    
    # Try to use Application Default Credentials first (for Cloud Run)
    try:
        credentials, project = default(scopes=SCOPES)
        print(f"✅ Using Application Default Credentials (project: {project})")
        return credentials
    except Exception as e:
        print(f"⚠️ Application Default Credentials not available: {e}")
        
        # Fallback to service account file for local development
        if not service_account_path.exists():
            raise FileNotFoundError(
                f"Service account file not found at {service_account_path}\n"
                "For local development: Please download the service account JSON key from Google Cloud Console "
                "and save it as configs/service_account.json\n"
                "For Cloud Run: Ensure the service account has Google Sheets API access"
            )
        
        print(f"📁 Using service account file: {service_account_path}")
        credentials = service_account.Credentials.from_service_account_file(
            str(service_account_path),
            scopes=SCOPES
        )
        
        return credentials


def read_range_a_to_u() -> List[List[str]]:
    """Read data from Google Sheets using service account authentication."""
    cfg = load_config()
    spreadsheet_id = cfg["spreadsheet_id"]
    sheet_name = cfg["sheet_name"]
    range_a1 = f"{sheet_name}!A:U"

    # Get service account credentials
    creds = get_credentials()
    
    # Build the Sheets service
    service = build("sheets", "v4", credentials=creds)
    sheet = service.spreadsheets()
    
    # Get the data
    result = sheet.values().get(spreadsheetId=spreadsheet_id, range=range_a1).execute()
    values = result.get("values", [])
    
    return values