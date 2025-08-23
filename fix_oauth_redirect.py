#!/usr/bin/env python3
"""
OAuth2 Redirect URI Fix Helper
"""

import sys
from pathlib import Path
import webbrowser

def main():
    """Help fix OAuth2 redirect URI mismatch error."""
    print("🔧 OAuth2 Redirect URI Fix Helper")
    print("=" * 50)
    
    print("🚨 Error: redirect_uri_mismatch")
    print("This means your Google Cloud Console OAuth2 settings don't match the app's redirect URI.")
    
    print(f"\n🔧 Quick Fix Steps:")
    print(f"   1. Go to Google Cloud Console")
    print(f"   2. Find your OAuth2 client")
    print(f"   3. Add redirect URI: http://localhost:8080/")
    print(f"   4. Save changes")
    print(f"   5. Delete existing token.json")
    print(f"   6. Try authentication again")
    
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
    
    print(f"\n🌐 Open Google Cloud Console?")
    response = input(f"   This will help you fix the redirect URI (y/n): ").lower().strip()
    if response in ['y', 'yes']:
        webbrowser.open("https://console.cloud.google.com/apis/credentials")
        print(f"   ✅ Opened Google Cloud Console")
        print(f"   📋 Look for your OAuth2 client and add redirect URI")
    
    print(f"\n📋 Required Redirect URI:")
    print(f"   http://localhost:8080/")
    
    print(f"\n🔍 Alternative URIs to try if the above doesn't work:")
    print(f"   http://127.0.0.1:8080/")
    print(f"   http://localhost:8080/oauth2callback")
    print(f"   http://127.0.0.1:8080/oauth2callback")
    
    print(f"\n✅ After fixing the redirect URI:")
    print(f"   1. Run: ./run_app.sh")
    print(f"   2. Click '手动刷新（读取 Google Sheet）'")
    print(f"   3. Complete OAuth authentication")
    
    print(f"\n📞 Need more help? Check docs/FIX_OAUTH_REDIRECT.md")


if __name__ == "__main__":
    main()
