# 🔧 Fix OAuth2 Web Application Configuration

## 🚨 Issue Found: Web Application Configuration

Your OAuth2 client is configured as a **Web application** instead of a **Desktop application**. This is causing the `redirect_uri_mismatch` error.

## 🔧 Solution: Convert to Desktop Application

### Option 1: Create New Desktop OAuth2 Client (Recommended)

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Navigate to **APIs & Services** > **Credentials**
3. Click **Create Credentials** > **OAuth 2.0 Client IDs**
4. Choose **Desktop application** (not Web application)
5. Give it a name (e.g., "Ministry Data Visualizer Desktop")
6. Click **Create**
7. Download the new JSON file
8. Replace your existing `client_secret.json` with the new one

### Option 2: Fix Existing Web Application

If you want to keep the existing client:

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Find your OAuth2 client (currently configured as Web application)
3. Click on it to edit
4. In **Authorized redirect URIs**, add:
   ```
   http://localhost:8080/
   http://127.0.0.1:8080/
   http://localhost:8080/oauth2callback
   http://127.0.0.1:8080/oauth2callback
   ```
5. Click **Save**

## 🎯 Why This Happens

- **Desktop applications** use `InstalledAppFlow` and don't require specific redirect URIs
- **Web applications** require exact redirect URI matching
- Your current client is configured as Web application but the code expects Desktop application

## 🧪 Test the Fix

After making changes:

```bash
# Test OAuth2 configuration
python test_oauth_config.py

# Run the app
./run_app.sh
```

## 📋 Expected Configuration

For Desktop application, your `client_secret.json` should look like:

```json
{
  "installed": {
    "client_id": "your-client-id.apps.googleusercontent.com",
    "project_id": "your-project-id",
    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
    "token_uri": "https://oauth2.googleapis.com/token",
    "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
    "client_secret": "your-client-secret",
    "redirect_uris": ["http://localhost"]
  }
}
```

## 🔄 Alternative: Update Code for Web Application

If you prefer to keep the Web application configuration, you can modify the code:

```python
# In ingest/sheets_client.py, change the OAuth flow:
from google_auth_oauthlib.flow import Flow

def get_credentials() -> Credentials:
    # ... existing code ...
    else:
        flow = Flow.from_client_secrets_file(
            "configs/client_secret.json", 
            SCOPES,
            redirect_uri="http://localhost:8080/"
        )
        creds = flow.run_local_server(port=8080)
```

## 🎯 Recommendation

**Use Option 1** (create new Desktop application) as it's simpler and more appropriate for this type of application.

## 📞 Next Steps

1. Create new Desktop OAuth2 client
2. Download and replace `client_secret.json`
3. Test with `python test_oauth_config.py`
4. Run the app with `./run_app.sh`
