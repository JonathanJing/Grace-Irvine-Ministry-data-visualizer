#!/usr/bin/env python3
"""
Google Service Account Setup Helper
"""

import sys
from pathlib import Path
import json
import webbrowser

def check_current_setup():
    """Check current authentication setup."""
    print("🔍 Current Authentication Setup")
    print("=" * 40)
    
    # Check for OAuth2 files
    client_secret_path = Path("configs/client_secret.json")
    token_path = Path("configs/token.json")
    service_account_path = Path("configs/service_account.json")
    
    print("OAuth2 Files:")
    print(f"  client_secret.json: {'✅ Found' if client_secret_path.exists() else '❌ Not found'}")
    print(f"  token.json: {'✅ Found' if token_path.exists() else '❌ Not found'}")
    
    print("\nService Account File:")
    print(f"  service_account.json: {'✅ Found' if service_account_path.exists() else '❌ Not found'}")
    
    return service_account_path.exists()

def check_service_account_file():
    """Check and validate service account JSON file."""
    print("\n🔍 Service Account File Check")
    print("=" * 40)
    
    service_account_path = Path("configs/service_account.json")
    
    if not service_account_path.exists():
        print("❌ service_account.json not found")
        return None
    
    try:
        with open(service_account_path, 'r') as f:
            sa_data = json.load(f)
        
        print("✅ service_account.json found and valid")
        
        # Check required fields
        required_fields = ['type', 'project_id', 'private_key', 'client_email']
        for field in required_fields:
            if field in sa_data:
                if field == 'private_key':
                    print(f"  ✅ {field}: present (hidden)")
                elif field == 'client_email':
                    print(f"  ✅ {field}: {sa_data[field]}")
                else:
                    print(f"  ✅ {field}: {sa_data[field]}")
            else:
                print(f"  ❌ {field}: missing")
        
        return sa_data.get('client_email')
        
    except json.JSONDecodeError:
        print("❌ Invalid JSON in service_account.json")
        return None
    except Exception as e:
        print(f"❌ Error reading service_account.json: {e}")
        return None

def setup_instructions():
    """Display setup instructions."""
    print("\n📋 Service Account Setup Instructions")
    print("=" * 40)
    
    print("\n1️⃣  Create Service Account in Google Cloud Console:")
    print("   a) Go to IAM & Admin > Service Accounts")
    print("   b) Click 'Create Service Account'")
    print("   c) Name it 'ministry-data-visualizer'")
    print("   d) Click 'Create and Continue'")
    print("   e) Skip optional steps, click 'Done'")
    
    print("\n2️⃣  Create and Download JSON Key:")
    print("   a) Click on the service account email")
    print("   b) Go to 'Keys' tab")
    print("   c) Click 'Add Key' > 'Create new key'")
    print("   d) Choose JSON format")
    print("   e) Click 'Create' to download")
    
    print("\n3️⃣  Configure the Application:")
    print("   a) Rename downloaded file to 'service_account.json'")
    print("   b) Move it to configs/ directory")
    
    response = input("\n🌐 Open Google Cloud Console? (y/n): ").lower().strip()
    if response in ['y', 'yes']:
        webbrowser.open("https://console.cloud.google.com/iam-admin/serviceaccounts")
        print("   ✅ Opened Service Accounts page")

def share_sheet_instructions(client_email):
    """Display instructions for sharing the Google Sheet."""
    print("\n📊 Share Google Sheet with Service Account")
    print("=" * 40)
    
    if client_email:
        print(f"\n⚠️  IMPORTANT: You must share your Google Sheet with:")
        print(f"   📧 {client_email}")
        print("\nSteps:")
        print("   1. Open your Google Sheet")
        print("   2. Click 'Share' button")
        print(f"   3. Add: {client_email}")
        print("   4. Give 'Viewer' permissions")
        print("   5. Click 'Send'")
    else:
        print("\n⚠️  Service account email not found")
        print("   Complete service account setup first")

def test_connection():
    """Test the service account connection."""
    print("\n🧪 Testing Service Account Connection")
    print("=" * 40)
    
    try:
        from ingest.sheets_client import get_credentials, read_range_a_to_u
        
        print("🔄 Getting credentials...")
        creds = get_credentials()
        print("✅ Credentials loaded successfully")
        
        print("🔄 Attempting to read Google Sheet...")
        values = read_range_a_to_u()
        
        if values:
            print(f"✅ Success! Retrieved {len(values)} rows")
            return True
        else:
            print("⚠️  Connected but no data found")
            return False
            
    except FileNotFoundError as e:
        print(f"❌ {e}")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        if "403" in str(e) or "Forbidden" in str(e):
            print("\n⚠️  Permission denied - Did you share the sheet with the service account?")
        return False

def main():
    """Main setup helper."""
    print("🔐 Google Service Account Setup Helper")
    print("=" * 50)
    
    print("\n🎯 Service Account Benefits:")
    print("  ✅ No OAuth2 authentication prompts")
    print("  ✅ No redirect URI configuration")
    print("  ✅ Works seamlessly in production")
    print("  ✅ More secure for automation")
    
    # Check current setup
    has_service_account = check_current_setup()
    
    if not has_service_account:
        # Show setup instructions
        setup_instructions()
        
        print("\n📝 After downloading the JSON key:")
        print("   1. Rename to 'service_account.json'")
        print("   2. Move to configs/ directory")
        print("   3. Run this script again")
    else:
        # Check service account file
        client_email = check_service_account_file()
        
        if client_email:
            # Show sharing instructions
            share_sheet_instructions(client_email)
            
            # Test connection
            response = input("\n🧪 Test the connection now? (y/n): ").lower().strip()
            if response in ['y', 'yes']:
                if test_connection():
                    print("\n✅ Service account is working perfectly!")
                    print("   You can now run: ./run_app.sh")
                else:
                    print("\n❌ Connection failed")
                    print("   Please check:")
                    print("   1. Sheet is shared with service account")
                    print("   2. Google Sheets API is enabled")
                    print("   3. Service account key is valid")
    
    print("\n📚 Documentation: docs/SERVICE_ACCOUNT_SETUP.md")
    print("🧪 Test script: python ingest/sheets_client_service_account.py")


if __name__ == "__main__":
    main()
