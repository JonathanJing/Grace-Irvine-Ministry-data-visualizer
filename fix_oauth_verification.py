#!/usr/bin/env python3
"""
Fix OAuth2 Verification and Access Denied Error
"""

import sys
from pathlib import Path
import webbrowser
import json

def main():
    """Help fix the OAuth2 verification and access_denied error."""
    print("🔧 OAuth2 Verification and Access Denied Fix")
    print("=" * 50)
    
    print("🚨 Error: access_denied - App Not Verified")
    print("   Your OAuth2 app is in testing mode and needs verification.")
    
    print(f"\n🔧 Quick Fix Steps:")
    print(f"   1. Add your email as a test user")
    print(f"   2. Use less sensitive OAuth2 scope")
    print(f"   3. Delete existing token")
    print(f"   4. Test authentication")
    
    # Check current scope
    sheets_client_path = Path("ingest/sheets_client.py")
    if sheets_client_path.exists():
        try:
            with open(sheets_client_path, 'r') as f:
                content = f.read()
            
            if "spreadsheets.readonly" in content:
                print(f"\n⚠️  Current scope: spreadsheets.readonly (sensitive)")
                print(f"   This requires Google verification")
                
                response = input(f"   Change to drive.readonly (less sensitive)? (y/n): ").lower().strip()
                if response in ['y', 'yes']:
                    # Update the scope
                    new_content = content.replace(
                        'SCOPES = ["https://www.googleapis.com/auth/spreadsheets.readonly"]',
                        'SCOPES = ["https://www.googleapis.com/auth/drive.readonly"]'
                    )
                    
                    with open(sheets_client_path, 'w') as f:
                        f.write(new_content)
                    
                    print(f"   ✅ Updated scope to drive.readonly")
                else:
                    print(f"   ℹ️  Keeping current scope")
            else:
                print(f"   ✅ Scope already set to drive.readonly")
        except Exception as e:
            print(f"   ❌ Error reading sheets_client.py: {e}")
    
    # Check for existing token
    token_path = Path("configs/token.json")
    if token_path.exists():
        print(f"\n⚠️  Found existing token.json")
        response = input(f"   Delete it to force re-authentication? (y/n): ").lower().strip()
        if response in ['y', 'yes']:
            token_path.unlink()
            print(f"   ✅ Deleted token.json")
        else:
            print(f"   ℹ️  Keeping existing token.json")
    
    print(f"\n🌐 Open Google Cloud Console OAuth Consent Screen?")
    response = input(f"   This will help you add test users (y/n): ").lower().strip()
    if response in ['y', 'yes']:
        webbrowser.open("https://console.cloud.google.com/apis/credentials/consent")
        print(f"   ✅ Opened OAuth Consent Screen")
        print(f"   📋 Steps:")
        print(f"      1. Scroll down to 'Test users' section")
        print(f"      2. Click 'Add Users'")
        print(f"      3. Add your Google email address")
        print(f"      4. Click 'Save'")
    
    print(f"\n📋 Alternative Solutions:")
    print(f"   1. Add your email as test user (recommended)")
    print(f"   2. Use drive.readonly scope (already applied)")
    print(f"   3. Publish app to production (takes weeks)")
    
    print(f"\n✅ After fixing:")
    print(f"   1. Test configuration: python test_oauth_config.py")
    print(f"   2. Run the app: ./run_app.sh")
    print(f"   3. Complete OAuth authentication")
    
    print(f"\n🔍 Why this happens:")
    print(f"   - Google requires verification for sensitive scopes")
    print(f"   - spreadsheets.readonly is considered sensitive")
    print(f"   - drive.readonly is less sensitive")
    print(f"   - Test users can access unverified apps")
    
    print(f"\n📞 Need more help? Check docs/FIX_OAUTH_VERIFICATION.md")


if __name__ == "__main__":
    main()
