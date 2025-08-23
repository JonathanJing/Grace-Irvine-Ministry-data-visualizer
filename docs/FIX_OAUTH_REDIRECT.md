# 🔧 Fix OAuth2 Redirect URI Mismatch Error

## 🚨 Error: `redirect_uri_mismatch`

This error occurs when the redirect URI in your Google Cloud Console doesn't match what the application is using.

## 🔧 Solution

### Step 1: Update Google Cloud Console OAuth2 Settings

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Navigate to **APIs & Services** > **Credentials**
3. Find your OAuth2 client ID and click on it
4. In the **Authorized redirect URIs** section, add:
   ```
   http://localhost:8081/
   ```
5. Click **Save**

### Step 2: Alternative Redirect URIs

If the above doesn't work, try these common redirect URIs:

```
http://localhost:8081/
http://127.0.0.1:8081/
http://localhost:8081/oauth2callback
http://127.0.0.1:8081/oauth2callback
```

### Step 3: Verify Your OAuth2 Client Type

Make sure your OAuth2 client is configured as:
- **Application type**: Desktop application
- **Not** Web application (which requires different redirect URIs)

### Step 4: Delete Existing Token

If you have an existing `token.json`, delete it to force re-authentication:

```bash
rm configs/token.json
```

### Step 5: Test Authentication

Run the authentication test:

```bash
python tests/simple_auth_test.py
```

## 🔍 Troubleshooting

### Check Current Redirect URIs

1. In Google Cloud Console, go to your OAuth2 client
2. Look at the **Authorized redirect URIs** section
3. Make sure `http://localhost:8080/` is listed

### Common Issues

1. **Wrong Application Type**: Make sure it's "Desktop application"
2. **Missing Redirect URI**: Add `http://localhost:8080/`
3. **Wrong Port**: The app now uses port 8080 (not random)
4. **Cached Token**: Delete `token.json` to force re-auth

### Alternative: Use Different Port

If port 8080 is busy, you can modify the code to use a different port:

```python
# In ingest/sheets_client.py, change line 32:
creds = flow.run_local_server(port=8081)  # or any available port
```

Then add the corresponding redirect URI in Google Cloud Console:
```
http://localhost:8081/
```

## 🧪 Test Your Fix

1. Update Google Cloud Console redirect URIs
2. Delete `configs/token.json` (if it exists)
3. Run the app: `./run_app.sh`
4. Click "手动刷新（读取 Google Sheet）"
5. Complete OAuth authentication

## 📞 Still Having Issues?

If you're still getting the error:

1. **Double-check redirect URIs** in Google Cloud Console
2. **Verify client type** is "Desktop application"
3. **Try a different port** (8081, 8082, etc.)
4. **Check for typos** in the redirect URI
5. **Wait a few minutes** - changes can take time to propagate

## 🔒 Security Note

The redirect URI `http://localhost:8080/` is safe for local development because:
- It only works on your local machine
- It's not accessible from the internet
- It's the standard for desktop OAuth2 applications
