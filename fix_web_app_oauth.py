#!/usr/bin/env python3
"""
Fix OAuth2 Web Application Configuration Issue
"""

import sys
from pathlib import Path
import webbrowser
import json

def main():
    """Help fix the OAuth2 web application configuration issue."""
    print("🔧 OAuth2 Web Application Configuration Fix")
    print("=" * 50)
    
    print("🚨 Issue Found: Your OAuth2 client is configured as a Web application")
    print("   This is causing the redirect_uri_mismatch error.")
    
    client_secret_path = Path("configs/client_secret.json")
    
    if client_secret_path.exists():
        try:
            with open(client_secret_path, 'r') as f:
                config = json.load(f)
            
            if 'web' in config:
                print("✅ Confirmed: Web application configuration detected")
                print("   This needs to be changed to Desktop application")
            elif 'installed' in config:
                print("✅ Good: Desktop application configuration detected")
                print("   Your configuration is already correct!")
                return
        except Exception as e:
            print(f"❌ Error reading client_secret.json: {e}")
    
    print(f"\n🔧 Solution Options:")
    print(f"   Option 1: Create new Desktop OAuth2 client (Recommended)")
    print(f"   Option 2: Fix existing Web application redirect URIs")
    
    print(f"\n🎯 Recommended: Option 1 - Create Desktop Application")
    print(f"   1. Go to Google Cloud Console")
    print(f"   2. Create new OAuth2 client (Desktop application)")
    print(f"   3. Download new client_secret.json")
    print(f"   4. Replace existing file")
    
    response = input(f"\n🌐 Open Google Cloud Console to create Desktop OAuth2 client? (y/n): ").lower().strip()
    if response in ['y', 'yes']:
        webbrowser.open("https://console.cloud.google.com/apis/credentials")
        print(f"   ✅ Opened Google Cloud Console")
        print(f"   📋 Steps:")
        print(f"      1. Click 'Create Credentials' > 'OAuth 2.0 Client IDs'")
        print(f"      2. Choose 'Desktop application'")
        print(f"      3. Give it a name (e.g., 'Ministry Data Visualizer Desktop')")
        print(f"      4. Click 'Create'")
        print(f"      5. Download the JSON file")
        print(f"      6. Replace configs/client_secret.json")
    
    print(f"\n📋 Alternative: Option 2 - Fix Web Application")
    print(f"   If you prefer to keep the existing client:")
    print(f"   1. Go to your existing OAuth2 client")
    print(f"   2. Add these redirect URIs:")
    print(f"      - http://localhost:8080/")
    print(f"      - http://127.0.0.1:8080/")
    print(f"      - http://localhost:8080/oauth2callback")
    print(f"      - http://127.0.0.1:8080/oauth2callback")
    
    print(f"\n✅ After fixing:")
    print(f"   1. Test configuration: python test_oauth_config.py")
    print(f"   2. Run the app: ./run_app.sh")
    print(f"   3. Complete OAuth authentication")
    
    print(f"\n📞 Need more help? Check docs/FIX_WEB_APP_OAUTH.md")


if __name__ == "__main__":
    main()
