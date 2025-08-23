#!/usr/bin/env python3
"""
Debug OAuth2 Authentication Issues
"""

import sys
from pathlib import Path
import json
import webbrowser

def check_oauth_config():
    """Check OAuth2 configuration."""
    print("🔍 OAuth2 Configuration Check")
    print("=" * 40)
    
    client_secret_path = Path("configs/client_secret.json")
    token_path = Path("configs/token.json")
    
    # Check client_secret.json
    if not client_secret_path.exists():
        print("❌ client_secret.json not found")
        return False
    
    try:
        with open(client_secret_path, 'r') as f:
            config = json.load(f)
        
        print("✅ client_secret.json found")
        
        # Check configuration type
        if 'installed' in config:
            print("✅ Desktop application configuration")
            client_info = config['installed']
        elif 'web' in config:
            print("⚠️  Web application configuration")
            client_info = config['web']
        else:
            print("❌ Unknown configuration type")
            return False
        
        # Check client info
        client_id = client_info.get('client_id', 'Unknown')
        project_id = client_info.get('project_id', 'Unknown')
        
        print(f"📋 Client ID: {client_id[:20]}...")
        print(f"📋 Project ID: {project_id}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error reading client_secret.json: {e}")
        return False

def check_token():
    """Check if token exists and is valid."""
    print(f"\n🔍 Token Check")
    print("=" * 40)
    
    token_path = Path("configs/token.json")
    
    if not token_path.exists():
        print("❌ token.json not found")
        print("   This means OAuth authentication didn't complete successfully")
        return False
    
    try:
        with open(token_path, 'r') as f:
            token_data = json.load(f)
        
        print("✅ token.json found")
        
        # Check token fields
        required_fields = ['token', 'refresh_token', 'token_uri', 'client_id', 'client_secret']
        for field in required_fields:
            if field in token_data:
                print(f"   ✅ {field}: present")
            else:
                print(f"   ❌ {field}: missing")
        
        return True
        
    except Exception as e:
        print(f"❌ Error reading token.json: {e}")
        return False

def test_oauth_flow():
    """Test the OAuth flow directly."""
    print(f"\n🧪 Testing OAuth Flow")
    print("=" * 40)
    
    try:
        from ingest.sheets_client import get_credentials
        
        print("🔄 Attempting to get credentials...")
        creds = get_credentials()
        
        if creds:
            print("✅ Credentials obtained successfully!")
            print(f"   Valid: {creds.valid}")
            print(f"   Expired: {creds.expired}")
            return True
        else:
            print("❌ Failed to get credentials")
            return False
            
    except Exception as e:
        print(f"❌ Error during OAuth flow: {e}")
        return False

def check_google_cloud_setup():
    """Check Google Cloud Console setup."""
    print(f"\n🌐 Google Cloud Console Setup")
    print("=" * 40)
    
    print("📋 Please verify these settings in Google Cloud Console:")
    print("   1. Go to: https://console.cloud.google.com/apis/credentials")
    print("   2. Check your OAuth2 client configuration")
    print("   3. Go to: https://console.cloud.google.com/apis/credentials/consent")
    print("   4. Verify test users are added")
    
    response = input(f"\n🌐 Open Google Cloud Console? (y/n): ").lower().strip()
    if response in ['y', 'yes']:
        webbrowser.open("https://console.cloud.google.com/apis/credentials")
        print("   ✅ Opened Google Cloud Console")
    
    return True

def main():
    """Main debugging function."""
    print("🔧 OAuth2 Authentication Debug")
    print("=" * 50)
    
    print("🚨 Issue: Authentication still failing after Google sign-in")
    print("   Let's identify the specific problem...")
    
    # Run checks
    config_ok = check_oauth_config()
    token_ok = check_token()
    
    if not config_ok:
        print(f"\n❌ OAuth2 configuration issue detected")
        print("   Please check your client_secret.json file")
        return
    
    if not token_ok:
        print(f"\n❌ Token issue detected")
        print("   OAuth authentication didn't complete successfully")
        
        # Test OAuth flow
        print(f"\n🔄 Testing OAuth flow...")
        flow_ok = test_oauth_flow()
        
        if not flow_ok:
            print(f"\n❌ OAuth flow failed")
            print("   This suggests an issue with the OAuth2 setup")
            
            # Check Google Cloud setup
            check_google_cloud_setup()
    
    print(f"\n📋 Common Issues and Solutions:")
    print("   1. OAuth2 client type: Should be 'Desktop application'")
    print("   2. Test users: Your email should be added as test user")
    print("   3. OAuth consent screen: Should be in 'Testing' mode")
    print("   4. Redirect URIs: Should include http://localhost:8080/")
    
    print(f"\n🔧 Quick Fixes to Try:")
    print("   1. Delete token.json: rm configs/token.json")
    print("   2. Check test user setup in Google Cloud Console")
    print("   3. Verify OAuth2 client is Desktop application")
    print("   4. Try authentication again")
    
    print(f"\n🧪 Test Commands:")
    print("   python test_oauth_config.py")
    print("   python tests/simple_auth_test.py")
    print("   ./run_app.sh")


if __name__ == "__main__":
    main()
