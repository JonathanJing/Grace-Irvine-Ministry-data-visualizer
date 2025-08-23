#!/usr/bin/env python3
"""
Fix OAuth2 Port Conflict Issue
"""

import sys
from pathlib import Path
import webbrowser

def main():
    """Help fix the OAuth2 port conflict issue."""
    print("🔧 OAuth2 Port Conflict Fix")
    print("=" * 40)
    
    print("🚨 Issue Found: Port 8080 is already in use")
    print("   This prevents OAuth2 authentication from working.")
    
    print(f"\n🔧 Solution Applied:")
    print(f"   ✅ Changed OAuth2 port from 8080 to 8081")
    print(f"   ✅ Updated ingest/sheets_client.py")
    
    print(f"\n📋 Next Steps:")
    print(f"   1. Update Google Cloud Console redirect URIs")
    print(f"   2. Add http://localhost:8081/ to your OAuth2 client")
    print(f"   3. Test authentication again")
    
    print(f"\n🌐 Open Google Cloud Console to update redirect URIs?")
    response = input(f"   This will help you add the new redirect URI (y/n): ").lower().strip()
    if response in ['y', 'yes']:
        webbrowser.open("https://console.cloud.google.com/apis/credentials")
        print(f"   ✅ Opened Google Cloud Console")
        print(f"   📋 Steps:")
        print(f"      1. Find your OAuth2 client")
        print(f"      2. Click on it to edit")
        print(f"      3. In 'Authorized redirect URIs', add:")
        print(f"         http://localhost:8081/")
        print(f"      4. Click 'Save'")
    
    print(f"\n📋 Required Redirect URIs:")
    print(f"   http://localhost:8081/")
    print(f"   http://127.0.0.1:8081/")
    
    print(f"\n🔍 Alternative Redirect URIs (if needed):")
    print(f"   http://localhost:8081/oauth2callback")
    print(f"   http://127.0.0.1:8081/oauth2callback")
    
    print(f"\n✅ After updating Google Cloud Console:")
    print(f"   1. Test OAuth2 configuration: python test_oauth_config.py")
    print(f"   2. Run the app: ./run_app.sh")
    print(f"   3. Click '手动刷新（读取 Google Sheet）'")
    print(f"   4. Complete OAuth authentication")
    
    print(f"\n🔧 Why This Happened:")
    print(f"   - Port 8080 was already in use by another process")
    print(f"   - OAuth2 needs an available port for the callback")
    print(f"   - Port 8081 should be available")
    
    print(f"\n📞 Need more help?")
    print(f"   - Check if port 8081 is available")
    print(f"   - Try a different port if needed (8082, 8083, etc.)")
    print(f"   - Update both code and Google Cloud Console")


if __name__ == "__main__":
    main()
