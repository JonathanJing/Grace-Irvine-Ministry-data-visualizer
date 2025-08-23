#!/usr/bin/env python3
"""
Test OAuth2 configuration and redirect URI setup.
"""

import json
from pathlib import Path

def test_oauth_config():
    """Test the OAuth2 configuration."""
    print("🔧 OAuth2 Configuration Test")
    print("=" * 40)
    
    client_secret_path = Path("configs/client_secret.json")
    
    if not client_secret_path.exists():
        print("❌ client_secret.json not found")
        return False
    
    try:
        with open(client_secret_path, 'r') as f:
            config = json.load(f)
        
        print("✅ client_secret.json found and valid JSON")
        
        # Check for required fields
        if 'installed' in config:
            print("✅ Desktop application configuration detected")
            client_info = config['installed']
        elif 'web' in config:
            print("⚠️  Web application configuration detected")
            print("   This might cause redirect URI issues")
            client_info = config['web']
        else:
            print("❌ Unknown OAuth2 configuration type")
            return False
        
        # Display client info
        client_id = client_info.get('client_id', 'Unknown')
        project_id = client_info.get('project_id', 'Unknown')
        
        print(f"📋 Client ID: {client_id[:20]}...")
        print(f"📋 Project ID: {project_id}")
        
        # Check redirect URIs
        if 'redirect_uris' in client_info:
            uris = client_info['redirect_uris']
            print(f"📋 Current redirect URIs:")
            for uri in uris:
                print(f"   - {uri}")
            
            # Check if localhost:8081 is included
            localhost_8081 = "http://localhost:8081/"
            if localhost_8081 in uris:
                print(f"✅ Required redirect URI found: {localhost_8081}")
            else:
                print(f"❌ Missing required redirect URI: {localhost_8081}")
                print(f"   Add this to your Google Cloud Console OAuth2 client")
                return False
        else:
            print("⚠️  No redirect URIs found in configuration")
            print("   This is normal for desktop applications")
        
        return True
        
    except json.JSONDecodeError as e:
        print(f"❌ Invalid JSON in client_secret.json: {e}")
        return False
    except Exception as e:
        print(f"❌ Error reading client_secret.json: {e}")
        return False


def main():
    """Run the OAuth2 configuration test."""
    success = test_oauth_config()
    
    print(f"\n📋 Summary:")
    if success:
        print("✅ OAuth2 configuration looks good!")
        print("   Try running the app now: ./run_app.sh")
    else:
        print("❌ OAuth2 configuration needs fixing")
        print("   Run: python fix_oauth_redirect.py")
        print("   Or check: docs/FIX_OAUTH_REDIRECT.md")


if __name__ == "__main__":
    main()
