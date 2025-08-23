# 🔐 Google Service Account Setup Guide

## 🎯 Why Service Account?

Service accounts are better for automated access because:
- ✅ No OAuth2 flows or user authentication prompts
- ✅ No redirect URIs to configure
- ✅ No token expiration issues
- ✅ Works seamlessly in production environments
- ✅ More secure for server-to-server communication

## 📋 Setup Steps

### Step 1: Create Service Account

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Navigate to **IAM & Admin** > **Service Accounts**
3. Click **Create Service Account**
4. Fill in the details:
   - **Service account name**: `ministry-data-visualizer`
   - **Service account ID**: (auto-generated)
   - **Description**: `Service account for Ministry Data Visualizer`
5. Click **Create and Continue**
6. Skip the optional steps (Grant access, Grant users access)
7. Click **Done**

### Step 2: Create and Download JSON Key

1. Find your new service account in the list
2. Click on the service account email
3. Go to the **Keys** tab
4. Click **Add Key** > **Create new key**
5. Choose **JSON** format
6. Click **Create**
7. The JSON key file will download automatically

### Step 3: Configure the Application

1. Rename the downloaded file to `service_account.json`
2. Move it to the `configs/` directory:
   ```bash
   mv ~/Downloads/[downloaded-file].json configs/service_account.json
   ```

### Step 4: Share Google Sheet with Service Account

**IMPORTANT**: You must share the Google Sheet with the service account email!

1. Open your Google Sheet
2. Click the **Share** button
3. Add the service account email (found in the JSON file as `client_email`)
   - It looks like: `service-account-name@project-id.iam.gserviceaccount.com`
4. Give it **Viewer** permissions (read-only)
5. Click **Send**

### Step 5: Test the Connection

```bash
# Test service account connection
python ingest/sheets_client_service_account.py

# Run the app
./run_app.sh
```

## 📝 Service Account JSON Structure

Your `service_account.json` should look like this:

```json
{
  "type": "service_account",
  "project_id": "your-project-id",
  "private_key_id": "key-id",
  "private_key": "-----BEGIN PRIVATE KEY-----\n...\n-----END PRIVATE KEY-----\n",
  "client_email": "service-account@project-id.iam.gserviceaccount.com",
  "client_id": "123456789",
  "auth_uri": "https://accounts.google.com/o/oauth2/auth",
  "token_uri": "https://oauth2.googleapis.com/token",
  "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
  "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/..."
}
```

## 🔍 Troubleshooting

### Common Issues

1. **"Service account file not found"**
   - Make sure `service_account.json` is in the `configs/` directory
   - Check the file name is exactly `service_account.json`

2. **"Permission denied" or "403 Forbidden"**
   - **Most common issue**: Forgot to share the Google Sheet with the service account email
   - Find the `client_email` in your `service_account.json`
   - Share the Google Sheet with that email address

3. **"Invalid grant" or authentication errors**
   - Check that the service account key is valid
   - Verify the project has Google Sheets API enabled

### Verify Setup

Run this command to test your service account:

```bash
python -c "from ingest.sheets_client import get_credentials; print('✅ Service account configured correctly!' if get_credentials() else '❌ Configuration error')"
```

## 🔒 Security Notes

- **Keep `service_account.json` secure** - it contains private keys
- **Already in `.gitignore`** - won't be committed to version control
- **Use read-only permissions** - only give the service account viewer access
- **Rotate keys periodically** - create new keys and delete old ones

## 🎯 Benefits Over OAuth2

| Feature | OAuth2 | Service Account |
|---------|--------|-----------------|
| User interaction | Required | Not needed |
| Token refresh | Required | Automatic |
| Redirect URIs | Must configure | Not needed |
| Production ready | Complex | Simple |
| Automation | Difficult | Easy |

## 📞 Quick Commands

```bash
# Test service account
python ingest/sheets_client_service_account.py

# Run the app
./run_app.sh

# Check if service account file exists
ls -la configs/service_account.json
```

## ✅ Checklist

- [ ] Created service account in Google Cloud Console
- [ ] Downloaded JSON key file
- [ ] Renamed to `service_account.json`
- [ ] Moved to `configs/` directory
- [ ] Shared Google Sheet with service account email
- [ ] Tested connection

Once all items are checked, your service account authentication is ready!
