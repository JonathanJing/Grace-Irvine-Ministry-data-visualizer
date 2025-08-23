#!/usr/bin/env python3
"""
Simple test to check Google Sheets authentication requirements.
"""

import sys
from pathlib import Path
import pandas as pd

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from ingest.sheets_client import load_config


def test_authentication_requirements():
    """Test what authentication is required for Google Sheets access."""
    print("🔐 Google Sheets Authentication Requirements Test")
    print("=" * 60)
    
    # Check config
    config_path = Path("configs/config.yaml")
    client_secret_path = Path("configs/client_secret.json")
    token_path = Path("configs/token.json")
    
    print(f"📋 Configuration:")
    print(f"   config.yaml: {'✅ Found' if config_path.exists() else '❌ Missing'}")
    print(f"   client_secret.json: {'✅ Found' if client_secret_path.exists() else '❌ Missing'}")
    print(f"   token.json: {'✅ Found' if token_path.exists() else '❌ Missing'}")
    
    if config_path.exists():
        config = load_config()
        spreadsheet_id = config.get("spreadsheet_id", "Unknown")
        sheet_name = config.get("sheet_name", "Unknown")
        print(f"   Spreadsheet ID: {spreadsheet_id}")
        print(f"   Sheet Name: {sheet_name}")
    
    print(f"\n🔍 Authentication Analysis:")
    
    # Check if authentication files exist
    has_auth_files = client_secret_path.exists() or token_path.exists()
    
    if has_auth_files:
        print("✅ Authentication files found - Google Sheets access should work")
        if client_secret_path.exists():
            print("   - client_secret.json: OAuth2 credentials available")
        if token_path.exists():
            print("   - token.json: Access token available (may need refresh)")
    else:
        print("❌ Authentication files missing - Google Sheets access will fail")
        print("\n📋 To enable Google Sheets access, you need:")
        print("   1. Google Cloud Project with Google Sheets API enabled")
        print("   2. OAuth2 credentials (client_secret.json)")
        print("   3. First-time authentication to generate token.json")
    
    # Test public access
    print(f"\n🌐 Testing Public Access:")
    if config_path.exists():
        config = load_config()
        spreadsheet_id = config.get("spreadsheet_id")
        
        if spreadsheet_id:
            public_url = f"https://docs.google.com/spreadsheets/d/{spreadsheet_id}/gviz/tq?tqx=out:csv"
            print(f"   Testing: {public_url}")
            
            try:
                # Try to read as CSV (public access)
                df = pd.read_csv(public_url)
                print(f"   ✅ Sheet is publicly accessible!")
                print(f"   📊 Data: {len(df)} rows, {len(df.columns)} columns")
                print(f"   📋 Columns: {list(df.columns)}")
                return True
            except Exception as e:
                print(f"   ❌ Sheet is not publicly accessible")
                print(f"   🔒 Error: {str(e)[:100]}...")
                print(f"   🔐 Authentication required for data access")
                return False
        else:
            print("   ❌ No spreadsheet_id found in config")
            return False
    else:
        print("   ❌ No config.yaml found")
        return False


def test_data_structure():
    """Test the expected data structure."""
    print(f"\n📊 Expected Data Structure:")
    
    config_path = Path("configs/config.yaml")
    if not config_path.exists():
        print("   ❌ config.yaml not found")
        return
    
    config = load_config()
    columns = config.get("columns", {})
    
    print(f"   📅 Date column: {columns.get('date', 'Unknown')}")
    print(f"   👥 Service roles:")
    
    roles = columns.get("roles", [])
    for role in roles:
        service_type = role.get("service_type", "Unknown")
        column_key = role.get("key", "Unknown")
        print(f"      - {service_type}: column {column_key}")


def main():
    """Run the authentication test."""
    print("🧪 Google Sheets Authentication Test")
    print("=" * 60)
    
    # Test authentication requirements
    is_public = test_authentication_requirements()
    
    # Test data structure
    test_data_structure()
    
    # Summary
    print(f"\n📋 SUMMARY:")
    if is_public:
        print("✅ Sheet is publicly accessible - no authentication needed!")
        print("   You can access data without OAuth2 credentials")
    else:
        print("❌ Sheet requires authentication")
        print("   You need OAuth2 credentials to access the data")
        print("\n🔧 Next steps:")
        print("   1. Get client_secret.json from Google Cloud Console")
        print("   2. Place it in configs/client_secret.json")
        print("   3. Run the app - it will prompt for authentication")
    
    print(f"\n" + "=" * 60)


if __name__ == "__main__":
    main()
