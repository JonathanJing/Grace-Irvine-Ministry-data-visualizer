# Google Sheets Authentication Requirements

## 🔐 Authentication Status

**❌ Authentication Required** - The Google Sheet is not publicly accessible and requires OAuth2 authentication.

## 📋 Current Status

- ✅ `config.yaml` - Found and valid
- ❌ `client_secret.json` - Missing (OAuth2 credentials)
- ❌ `token.json` - Missing (access token)

## 🎯 Answer: Yes, Secrets Are Required

**Yes, you need authentication secrets to read data from this Google Sheet.** The sheet is not publicly accessible, so you must use OAuth2 authentication.

## 🔧 Setup Instructions

### Step 1: Create Google Cloud Project

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select an existing one
3. Enable the **Google Sheets API**:
   - Go to "APIs & Services" > "Library"
   - Search for "Google Sheets API"
   - Click "Enable"

### Step 2: Create OAuth2 Credentials

1. Go to "APIs & Services" > "Credentials"
2. Click "Create Credentials" > "OAuth 2.0 Client IDs"
3. Choose "Desktop application" as the application type
4. Give it a name (e.g., "Ministry Data Visualizer")
5. Click "Create"
6. Download the JSON file

### Step 3: Set Up Credentials

1. Rename the downloaded file to `client_secret.json`
2. Place it in the `configs/` directory:
   ```
   configs/client_secret.json
   ```

### Step 4: First Authentication

1. Run the app: `./run_app.sh`
2. When prompted, click "手动刷新（读取 Google Sheet）"
3. A browser window will open for Google OAuth authentication
4. Sign in with the Google account that has access to the sheet
5. Grant permissions to the application
6. The `token.json` file will be automatically created

## 📊 Sheet Information

- **Spreadsheet ID**: `1wescUQe9rIVLNcKdqmSLpzlAw9BGXMZmkFvjEF296nM`
- **Sheet Name**: `总表`
- **Required Columns**: A, Q, R, S, T, U
- **Service Types**: 音控, 导播, 摄影, ProPresenter播放, ProPresenter更新

## 🧪 Testing

Run the authentication test to verify your setup:

```bash
python tests/simple_auth_test.py
```

## 🔒 Security Notes

- `client_secret.json` contains sensitive credentials - keep it secure
- `token.json` contains access tokens - also keep secure
- Both files are already in `.gitignore` to prevent accidental commits
- Tokens expire and need to be refreshed periodically

## 🚀 Alternative: Make Sheet Public

If you want to avoid authentication, you can make the Google Sheet publicly accessible:

1. Open the Google Sheet
2. Click "Share" in the top right
3. Click "Change to anyone with the link"
4. Set permissions to "Viewer"
5. Copy the link

However, this makes the data publicly visible, which may not be desirable for ministry data.

## 📝 File Structure

```
configs/
├── config.yaml          # ✅ Configuration (exists)
├── client_secret.json   # ❌ OAuth2 credentials (needed)
└── token.json          # ❌ Access token (auto-generated)
```

## 🔄 Troubleshooting

### Common Issues

1. **"client_secret.json not found"**
   - Download OAuth2 credentials from Google Cloud Console
   - Place in `configs/client_secret.json`

2. **"Authentication failed"**
   - Check that the Google account has access to the sheet
   - Delete `token.json` and re-authenticate

3. **"Token expired"**
   - Delete `token.json` and re-authenticate
   - The app will automatically refresh tokens when possible

### Test Commands

```bash
# Test authentication setup
python tests/simple_auth_test.py

# Test full app functionality
./run_app.sh
```

## 📞 Support

If you encounter issues:
1. Check the authentication test output
2. Verify Google Cloud Project setup
3. Ensure the Google account has access to the sheet
4. Check that all required files are in the correct locations
