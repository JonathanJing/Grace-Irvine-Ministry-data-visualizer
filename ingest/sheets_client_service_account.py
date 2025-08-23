from __future__ import annotations

from typing import List
from pathlib import Path

import yaml
from google.oauth2 import service_account
from googleapiclient.discovery import build


# Scopes for Google Sheets read access
SCOPES = ["https://www.googleapis.com/auth/spreadsheets.readonly"]


def load_config() -> dict:
    with open("configs/config.yaml", "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def get_service_account_credentials():
    """Get credentials from service account JSON file."""
    service_account_path = Path("configs/service_account.json")
    
    if not service_account_path.exists():
        raise FileNotFoundError(
            f"Service account file not found at {service_account_path}\n"
            "Please download the service account JSON key from Google Cloud Console "
            "and save it as configs/service_account.json"
        )
    
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
    creds = get_service_account_credentials()
    
    # Build the Sheets service
    service = build("sheets", "v4", credentials=creds)
    sheet = service.spreadsheets()
    
    # Get the data
    result = sheet.values().get(spreadsheetId=spreadsheet_id, range=range_a1).execute()
    values = result.get("values", [])
    
    return values


def test_connection():
    """Test the service account connection to Google Sheets."""
    try:
        print("🔄 Testing service account connection...")
        
        # Get credentials
        creds = get_service_account_credentials()
        print("✅ Service account credentials loaded")
        
        # Load config
        cfg = load_config()
        spreadsheet_id = cfg["spreadsheet_id"]
        print(f"📋 Spreadsheet ID: {spreadsheet_id}")
        
        # Try to read data
        values = read_range_a_to_u()
        
        if values:
            print(f"✅ Successfully connected to Google Sheets!")
            print(f"   Retrieved {len(values)} rows of data")
            if len(values) > 0:
                print(f"   First row has {len(values[0])} columns")
            return True
        else:
            print("⚠️  Connected but no data found in sheet")
            return False
            
    except FileNotFoundError as e:
        print(f"❌ {e}")
        return False
    except Exception as e:
        print(f"❌ Connection failed: {e}")
        return False


if __name__ == "__main__":
    # Test the service account connection
    test_connection()
