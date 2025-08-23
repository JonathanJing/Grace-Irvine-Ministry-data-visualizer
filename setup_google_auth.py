#!/usr/bin/env python3
"""
Google Sheets Authentication Setup Helper
"""

import sys
from pathlib import Path
import webbrowser

def main():
    """Help user set up Google Sheets authentication."""
    print("🔐 Google Sheets Authentication Setup")
    print("=" * 50)
    
    config_dir = Path("configs")
    client_secret_path = config_dir / "client_secret.json"
    token_path = config_dir / "token.json"
    
    print(f"📋 Current Status:")
    print(f"   client_secret.json: {'✅ Found' if client_secret_path.exists() else '❌ Missing'}")
    print(f"   token.json: {'✅ Found' if token_path.exists() else '❌ Missing'}")
    
    if client_secret_path.exists() and token_path.exists():
        print("\n✅ Authentication is already set up!")
        print("   You can run the app with: ./run_app.sh")
        return
    
    print(f"\n🔧 Setup Instructions:")
    print(f"   1. Go to Google Cloud Console")
    print(f"   2. Create OAuth2 credentials")
    print(f"   3. Download client_secret.json")
    print(f"   4. Place it in configs/ directory")
    
    # Check if client_secret.json exists
    if not client_secret_path.exists():
        print(f"\n❌ client_secret.json is missing")
        print(f"   Please follow these steps:")
        print(f"   1. Go to: https://console.cloud.google.com/")
        print(f"   2. Create a new project or select existing")
        print(f"   3. Enable Google Sheets API")
        print(f"   4. Create OAuth2 credentials (Desktop app)")
        print(f"   5. Download the JSON file")
        print(f"   6. Rename to 'client_secret.json'")
        print(f"   7. Place in: {client_secret_path}")
        
        # Offer to open Google Cloud Console
        response = input(f"\n🌐 Open Google Cloud Console? (y/n): ").lower().strip()
        if response in ['y', 'yes']:
            webbrowser.open("https://console.cloud.google.com/")
            print(f"   Opened Google Cloud Console in your browser")
    
    # Check if token.json exists
    if not token_path.exists() and client_secret_path.exists():
        print(f"\n✅ client_secret.json found!")
        print(f"   Next step: Run the app to authenticate")
        print(f"   Command: ./run_app.sh")
        print(f"   Then click '手动刷新（读取 Google Sheet）'")
    
    print(f"\n📝 File locations:")
    print(f"   Expected: {client_secret_path}")
    print(f"   Expected: {token_path} (auto-generated)")
    
    print(f"\n🔒 Security reminder:")
    print(f"   - Keep client_secret.json secure")
    print(f"   - Don't commit it to version control")
    print(f"   - It's already in .gitignore")


if __name__ == "__main__":
    main()
