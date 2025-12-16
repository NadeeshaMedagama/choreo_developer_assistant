# How to Add Google Vision Credentials to Choreo

## Problem
The Google Cloud Vision API requires a service account JSON file, but Choreo doesn't support uploading files directly as secrets.

## Solution
Convert the JSON file to a single-line string and add it as an environment variable.

## Steps

### 1. Get Your Google Service Account JSON

Your credential file is located at:
```
~/Downloads/google-vision-credentials.json
```

**Example filename:** `google-vision-credentials.json` (use your actual credential file name)

### 2. Convert to Single-Line String

**Option A: Using Command Line**
cd ~/Downloads
# Navigate to the file location
cd /home/nadeeshame/Downloads
cat google-vision-credentials.json | jq -c . | xclip -selection clipboard
# Convert to single-line string and copy to clipboard
cat google-vision-credentials.json | jq -c .
# Or without xclip:
cat google-vision-credentials.json | jq -c .
```

**Option B: Using Python**
```python
import json
with open('~/Downloads/google-vision-credentials.json', 'r') as f:
# Read the JSON file
with open('~/Downloads/google-vision-credentials.json', 'r') as f:
    creds = json.load(f)

# Convert to single-line string
single_line = json.dumps(creds)
print(single_line)
```

**Option C: Manual (Quick)**
cat google-vision-credentials.json | tr -d '\n'
# Just remove all newlines
cat google-vision-credentials.json | tr -d '\n'
```

### 3. Add to Choreo

#### Method 1: Environment Variable (Recommended)

1. Go to **Choreo Console** → Your Component
2. Navigate to **DevOps** → **Configs & Secrets**
3. Click **Add Config**
4. Set:
   - **Name**: `GOOGLE_CREDENTIALS_JSON`
   - **Value**: Paste the single-line JSON string
   - **Type**: Config (or Secret for better security)
5. Save and redeploy

#### Method 2: Secret Store (Most Secure)

1. Go to **Choreo Console** → Your Component
2. Navigate to **DevOps** → **Secrets**
3. Click **Create Secret**
4. Set:
   - **Secret Name**: `google-vision-credentials`
   - **Key**: `GOOGLE_CREDENTIALS_JSON`
   - **Value**: Paste the single-line JSON string
5. Mount secret to component
6. Redeploy

### 4. Verify in Choreo

After deployment, check the logs to confirm credentials are loaded:

```bash
# Look for this in logs:
✓ Google Vision credentials loaded successfully
```

### 5. Test the API

Test that diagram processing works:

```bash
curl -X POST https://your-component-url.choreo.dev/api/process-diagram \
  -H "Content-Type: application/json" \
  -d '{
    "file_url": "https://example.com/diagram.png"
  }'
```

## Example Single-Line JSON

{"type":"service_account","project_id":"your-project-id","private_key_id":"your-key-id...","private_key":"-----BEGIN PRIVATE KEY-----\n...","client_email":"your-service-account@your-project.iam.gserviceaccount.com","client_id":"...","auth_uri":"https://accounts.google.com/o/oauth2/auth","token_uri":"https://oauth2.googleapis.com/token","auth_provider_x509_cert_url":"https://www.googleapis.com/oauth2/v1/certs","client_x509_cert_url":"..."}
```json
{"type":"service_account","project_id":"your-project-id","private_key_id":"your-key-id...","private_key":"-----BEGIN PRIVATE KEY-----\n...","client_email":"...","client_id":"...","auth_uri":"https://accounts.google.com/o/oauth2/auth","token_uri":"https://oauth2.googleapis.com/token","auth_provider_x509_cert_url":"https://www.googleapis.com/oauth2/v1/certs","client_x509_cert_url":"..."}
```

## Troubleshooting

### Issue: "Invalid JSON format"
**Solution**: Ensure there are no extra spaces or line breaks. Use `jq -c .` to compact it.

### Issue: "Private key format error"
**Solution**: Make sure `\n` characters in the private key are preserved in the JSON string.

### Issue: "Credentials not found"
**Solution**: Check that the environment variable name is exactly `GOOGLE_CREDENTIALS_JSON` (case-sensitive).

### Issue: "Permission denied"
**Solution**: Verify the service account has "Cloud Vision API User" role in Google Cloud Console.

## Security Best Practices

1. ✅ **Use Choreo Secrets** instead of regular configs for sensitive data
2. ✅ **Rotate credentials** regularly
3. ✅ **Limit service account permissions** to only what's needed (Vision API)
4. ❌ **Never commit** credentials to Git
5. ❌ **Never log** the credential content

## Alternative: Skip Google Vision

If you don't need OCR for images/diagrams, you can skip Google Vision:

1. Remove `GOOGLE_CREDENTIALS_JSON` from environment
2. The app will work without diagram OCR functionality
## Converting Your Credentials File

## Converting Your Specific File

Run this command to prepare your credentials:
# Replace 'google-vision-credentials.json' with your actual filename
CREDS_FILE=~/Downloads/google-vision-credentials.json


cat $CREDS_FILE | jq -c . > /tmp/google-creds-single-line.txt
# Convert and save to a file for easy copying
cat ~/Downloads/google-vision-credentials.json | jq -c . > /tmp/google-creds-single-line.txt

# Display for copying
cat /tmp/google-creds-single-line.txt
```

Then copy the output and paste it into Choreo as `GOOGLE_CREDENTIALS_JSON`.

