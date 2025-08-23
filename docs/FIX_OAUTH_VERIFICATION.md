# 🔧 Fix OAuth2 Verification and Access Denied Error

## 🚨 Error: `access_denied` - App Not Verified

This error occurs because your Google Cloud OAuth2 application hasn't been verified by Google and is in testing mode.

## 🔧 Solutions

### Option 1: Add Test Users (Quick Fix)

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Navigate to **APIs & Services** > **OAuth consent screen**
3. Scroll down to **Test users** section
4. Click **Add Users**
5. Add your Google email address (the one you're using to sign in)
6. Click **Save**

### Option 2: Use Less Sensitive Scopes

Modify the OAuth2 scopes to use less sensitive permissions:

```python
# In ingest/sheets_client.py, change line 12:
SCOPES = ["https://www.googleapis.com/auth/drive.readonly"]
```

Instead of:
```python
SCOPES = ["https://www.googleapis.com/auth/spreadsheets.readonly"]
```

### Option 3: Publish Your App (Advanced)

If you want to make the app available to all users:

1. Go to **OAuth consent screen**
2. Change **Publishing status** from "Testing" to "In production"
3. Complete Google's verification process (can take weeks)

## 🎯 Recommended: Option 1 + Option 2

### Step 1: Add Yourself as Test User

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Navigate to **APIs & Services** > **OAuth consent screen**
3. In **Test users** section, click **Add Users**
4. Add your Google email address
5. Click **Save**

### Step 2: Use Less Sensitive Scope

Update your `ingest/sheets_client.py`:

```python
# Change this line:
SCOPES = ["https://www.googleapis.com/auth/spreadsheets.readonly"]

# To this:
SCOPES = ["https://www.googleapis.com/auth/drive.readonly"]
```

### Step 3: Delete Existing Token

```bash
rm configs/token.json
```

### Step 4: Test Authentication

```bash
python test_oauth_config.py
./run_app.sh
```

## 🔍 Why This Happens

- Google requires OAuth2 apps to be verified for sensitive scopes
- `spreadsheets.readonly` is considered sensitive
- `drive.readonly` is less sensitive and often works without verification
- Test users can access unverified apps

## 📋 OAuth Consent Screen Settings

### For Testing (Recommended)
- **Publishing status**: Testing
- **User Type**: External
- **Test users**: Add your email address

### For Production
- **Publishing status**: In production
- **User Type**: External
- **Verification**: Required (takes weeks)

## 🧪 Test Your Fix

After making changes:

```bash
# Delete existing token
rm configs/token.json

# Test configuration
python test_oauth_config.py

# Run the app
./run_app.sh
```

## 🔄 Alternative: Use Service Account

If OAuth2 continues to be problematic, consider using a Service Account:

1. Create a Service Account in Google Cloud Console
2. Download the JSON key file
3. Share the Google Sheet with the service account email
4. Use service account authentication instead of OAuth2

## 📞 Troubleshooting

### Common Issues

1. **"Still getting access_denied"**
   - Make sure you added your email as a test user
   - Check that you're using the same email for authentication

2. **"Scope not working"**
   - Try `drive.readonly` instead of `spreadsheets.readonly`
   - Both scopes can access Google Sheets

3. **"Token still cached"**
   - Delete `token.json` to force re-authentication

### Test Commands

```bash
# Check OAuth2 configuration
python test_oauth_config.py

# Test authentication
python tests/simple_auth_test.py

# Run the app
./run_app.sh
```

## 🎯 Quick Fix Summary

1. **Add your email as test user** in OAuth consent screen
2. **Use `drive.readonly` scope** instead of `spreadsheets.readonly`
3. **Delete `token.json`** to force re-authentication
4. **Test the app** with `./run_app.sh`

This should resolve the verification and access denied errors.
