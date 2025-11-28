# GCP Setup Guide for RFP Accelerator Agent
## Gemini Enterprise Deployment

This guide walks you through setting up your GCP project (`gcp-sandpit-intelia`) to run the RFP Accelerator Agent with Gemini Enterprise.

---

## 📋 Prerequisites

- GCP Project: `gcp-sandpit-intelia`
- Gemini Enterprise access enabled
- Admin access to the GCP project
- gcloud CLI installed ([Install Guide](https://cloud.google.com/sdk/docs/install))

---

## 🚀 Step-by-Step Setup

### Step 1: Configure gcloud CLI

```powershell
# Set your active project
gcloud config set project gcp-sandpit-intelia

# Verify the project is set
gcloud config get-value project

# Authenticate (this will open a browser)
gcloud auth login

# Set up application default credentials for local development
gcloud auth application-default login
```

**Expected Output:**
```
Updated property [core/project].
gcp-sandpit-intelia
Credentials saved to: C:\Users\[YourUser]\AppData\Roaming\gcloud\...
```

---

### Step 2: Enable Required APIs

Enable all necessary Google Cloud APIs:

```powershell
# Enable Google Drive API
gcloud services enable drive.googleapis.com

# Enable Google Docs API
gcloud services enable docs.googleapis.com

# Enable Gmail API (for notifications)
gcloud services enable gmail.googleapis.com

# Enable Vertex AI API (for Gemini)
gcloud services enable aiplatform.googleapis.com

# Enable Cloud Logging API (for monitoring)
gcloud services enable logging.googleapis.com

# Enable all at once (alternative)
gcloud services enable drive.googleapis.com docs.googleapis.com gmail.googleapis.com aiplatform.googleapis.com logging.googleapis.com
```

**Verify APIs are enabled:**
```powershell
gcloud services list --enabled | Select-String -Pattern "drive|docs|gmail|aiplatform"
```

---

### Step 3: Create a Service Account (Recommended for Production)

For production use, create a dedicated service account:

```powershell
# Create service account
gcloud iam service-accounts create rfp-accelerator-agent `
  --display-name="RFP Accelerator Agent" `
  --description="Service account for RFP Accelerator Agent automation"

# Verify creation
gcloud iam service-accounts list | Select-String "rfp-accelerator"
```

**Expected Output:**
```
Created service account [rfp-accelerator-agent].
rfp-accelerator-agent@gcp-sandpit-intelia.iam.gserviceaccount.com
```

---

### Step 4: Grant Required IAM Roles

Grant the service account necessary permissions:

```powershell
# Set variables
$PROJECT_ID = "gcp-sandpit-intelia"
$SA_EMAIL = "rfp-accelerator-agent@gcp-sandpit-intelia.iam.gserviceaccount.com"

# Grant Vertex AI User role (for Gemini access)
gcloud projects add-iam-policy-binding $PROJECT_ID `
  --member="serviceAccount:$SA_EMAIL" `
  --role="roles/aiplatform.user"

# Grant Storage Object Viewer (if using GCS for knowledge base)
gcloud projects add-iam-policy-binding $PROJECT_ID `
  --member="serviceAccount:$SA_EMAIL" `
  --role="roles/storage.objectViewer"

# Grant Logging Writer (for Cloud Logging)
gcloud projects add-iam-policy-binding $PROJECT_ID `
  --member="serviceAccount:$SA_EMAIL" `
  --role="roles/logging.logWriter"
```

**Note:** For Google Drive, Docs, and Gmail APIs, you'll need to use domain-wide delegation (see Step 6) or use user credentials.

---

### Step 5: Create and Download Service Account Key

```powershell
# Create credentials directory
New-Item -ItemType Directory -Path ".\credentials" -Force

# Create and download key
gcloud iam service-accounts keys create credentials\rfp-agent-key.json `
  --iam-account=rfp-accelerator-agent@gcp-sandpit-intelia.iam.gserviceaccount.com

# Verify key was created
Get-Item credentials\rfp-agent-key.json
```

**⚠️ Security Warning:** Keep this key file secure! Add `credentials/` to `.gitignore` (already done).

---

### Step 6: Configure Google Workspace APIs (For Drive, Docs, Gmail)

Since Drive, Docs, and Gmail APIs require user context, you have two options:

#### **Option A: Use User Credentials (Recommended for Development)**

```powershell
# Already done in Step 1
gcloud auth application-default login
```

This uses your personal Google Workspace account for API calls.

#### **Option B: Domain-Wide Delegation (For Production)**

If you have Google Workspace admin access:

1. **Enable Domain-Wide Delegation for Service Account:**
   ```powershell
   # Get the service account's unique ID
   gcloud iam service-accounts describe rfp-accelerator-agent@gcp-sandpit-intelia.iam.gserviceaccount.com `
     --format="value(uniqueId)"
   ```

2. **In Google Workspace Admin Console:**
   - Go to: Security → API Controls → Domain-wide Delegation
   - Click "Add new"
   - Enter the Client ID (unique ID from above)
   - Add OAuth Scopes:
     ```
     https://www.googleapis.com/auth/drive
     https://www.googleapis.com/auth/documents
     https://www.googleapis.com/auth/gmail.send
     ```

3. **Update your code to use domain-wide delegation** (modify `integrations/*.py` files)

---

### Step 7: Verify Gemini Enterprise Access

Check if Gemini is available in your project:

```powershell
# List available models
gcloud ai models list --region=us-central1 --project=gcp-sandpit-intelia
```

**Expected Output:** Should show Gemini models like `gemini-1.5-pro-002`

If not available:
1. Ensure Gemini Enterprise is enabled for your organization
2. Contact your GCP account manager
3. Check [Vertex AI Gemini availability](https://cloud.google.com/vertex-ai/generative-ai/docs/learn/locations)

---

### Step 8: Set Up Environment Variables

Create a `.env` file (optional, for easier configuration):

```powershell
# Create .env file
@"
GOOGLE_APPLICATION_CREDENTIALS=credentials/rfp-agent-key.json
GCP_PROJECT=gcp-sandpit-intelia
GEMINI_MODEL=gemini-1.5-pro-002
GCP_REGION=us-central1
"@ | Out-File -FilePath .env -Encoding utf8
```

Or set environment variables directly:

```powershell
# Set for current session
$env:GOOGLE_APPLICATION_CREDENTIALS = "credentials\rfp-agent-key.json"
$env:GCP_PROJECT = "gcp-sandpit-intelia"

# Set permanently (Windows)
[System.Environment]::SetEnvironmentVariable('GOOGLE_APPLICATION_CREDENTIALS', 'credentials\rfp-agent-key.json', 'User')
[System.Environment]::SetEnvironmentVariable('GCP_PROJECT', 'gcp-sandpit-intelia', 'User')
```

---

### Step 9: Configure the Application

Edit `config.yaml`:

```powershell
# Copy example config
Copy-Item config.example.yaml config.yaml

# Edit config.yaml
notepad config.yaml
```

**Update these values:**

```yaml
# GCP Project Settings
gcp_project: "gcp-sandpit-intelia"
gcp_region: "us-central1"

# Gemini AI Settings
gemini_model: "gemini-1.5-pro-002"
gemini_temperature: 0.7
gemini_max_tokens: 8192

# Email Notification Settings
email_enabled: true
email_sender: "your-email@yourdomain.com"  # Your Google Workspace email

# Company Information (for draft answers)
company_info:
  name: "Your Company Name"
  address: "Your Address"
  phone: "+1 (555) 123-4567"
  email: "contact@yourcompany.com"
  website: "https://www.yourcompany.com"
```

---

### Step 10: Install Python Dependencies

```powershell
# Activate virtual environment (if not already activated)
.\venv\Scripts\Activate

# Install dependencies
pip install -r requirements.txt

# Verify installation
python -c "from rfp_agent import RFPAcceleratorAgent; print('✓ Installation successful')"
```

---

### Step 11: Test the Setup

Run a quick test to verify everything is configured:

```powershell
# Test authentication
python -c "from google.cloud import aiplatform; aiplatform.init(project='gcp-sandpit-intelia', location='us-central1'); print('✓ Vertex AI connection successful')"

# Test Gemini access
python -c "from vertexai.generative_models import GenerativeModel; model = GenerativeModel('gemini-1.5-pro-002'); print('✓ Gemini model accessible')"

# Check agent status
python main.py status
```

---

### Step 12: Create a Test Google Drive Folder (Optional)

Create a parent folder for all RFP projects:

1. Go to [Google Drive](https://drive.google.com)
2. Create a new folder: "RFP Projects"
3. Right-click → "Get link" → Copy the folder ID from the URL
   - URL format: `https://drive.google.com/drive/folders/[FOLDER_ID]`
4. Update `config.yaml`:
   ```yaml
   drive_parent_folder_id: "[FOLDER_ID]"
   ```

---

## 🧪 Test Run

Now test the agent with a sample RFP:

```powershell
# Create a test RFP file (or use a real one)
@"
REQUEST FOR PROPOSAL
Acme Corporation
Digital Transformation Initiative
RFP #2024-001

We are seeking proposals for a comprehensive digital transformation...

Deadline: December 31, 2024
"@ | Out-File -FilePath test_rfp.txt -Encoding utf8

# Run the agent
python main.py run `
  -f "test_rfp.txt" `
  -c "Acme Corporation" `
  -t "Digital Transformation" `
  -m "your-email@yourdomain.com"
```

**Expected Output:**
- ✅ Project folder created in Google Drive
- ✅ Questions document generated
- ✅ Draft answers document generated
- ✅ Project plan document generated
- ✅ Email notification sent

---

## 🔍 Verification Checklist

- [ ] gcloud CLI configured with correct project
- [ ] All required APIs enabled
- [ ] Service account created (or using user credentials)
- [ ] IAM roles granted
- [ ] Service account key downloaded (if using service account)
- [ ] Gemini Enterprise access verified
- [ ] Environment variables set
- [ ] config.yaml configured
- [ ] Python dependencies installed
- [ ] Test run successful

---

## 🐛 Troubleshooting

### Issue: "Permission Denied" errors

**Solution:**
```powershell
# Re-authenticate
gcloud auth application-default login

# Verify credentials
gcloud auth application-default print-access-token
```

### Issue: "API not enabled"

**Solution:**
```powershell
# Check which APIs are enabled
gcloud services list --enabled

# Enable missing API
gcloud services enable [API_NAME].googleapis.com
```

### Issue: "Gemini model not found"

**Solution:**
```powershell
# Check available models in your region
gcloud ai models list --region=us-central1

# Try a different region
gcloud ai models list --region=us-east1

# Update config.yaml with correct region and model
```

### Issue: "Cannot access Google Drive/Docs"

**Solution:**
- Ensure you're using user credentials: `gcloud auth application-default login`
- Or set up domain-wide delegation (see Step 6)
- Check that you have access to Google Drive in your browser

### Issue: "Email notifications not working"

**Solution:**
```powershell
# Verify Gmail API is enabled
gcloud services list --enabled | Select-String "gmail"

# Check sender email in config.yaml matches your authenticated account
```

---

## 📊 Monitoring & Logs

### View Cloud Logs

```powershell
# View recent logs
gcloud logging read "resource.type=global" --limit=50 --format=json

# Filter by service
gcloud logging read "resource.type=global AND jsonPayload.service=rfp-agent" --limit=20
```

### View Vertex AI Usage

```powershell
# Check Vertex AI quotas
gcloud ai quotas list --region=us-central1
```

---

## 🔐 Security Best Practices

1. **Never commit credentials:**
   - ✅ `.gitignore` already includes `credentials/` and `*.json`
   
2. **Rotate service account keys regularly:**
   ```powershell
   # Delete old key
   gcloud iam service-accounts keys delete [KEY_ID] --iam-account=[SA_EMAIL]
   
   # Create new key
   gcloud iam service-accounts keys create credentials/rfp-agent-key.json --iam-account=[SA_EMAIL]
   ```

3. **Use least privilege:**
   - Only grant necessary IAM roles
   - Use separate service accounts for different environments

4. **Enable audit logging:**
   ```powershell
   gcloud logging read "protoPayload.serviceName=aiplatform.googleapis.com" --limit=10
   ```

---

## 🚀 Production Deployment

For production deployment:

1. **Use Cloud Run or Cloud Functions:**
   ```powershell
   # Deploy to Cloud Run
   gcloud run deploy rfp-agent --source . --region us-central1
   ```

2. **Set up Cloud Scheduler for automated runs**

3. **Use Secret Manager for credentials:**
   ```powershell
   # Store credentials in Secret Manager
   gcloud secrets create rfp-agent-config --data-file=config.yaml
   ```

4. **Enable Cloud Monitoring and Alerting**

---

## 📞 Support

If you encounter issues:

1. Check the [Troubleshooting](#-troubleshooting) section
2. Review [GCP Documentation](https://cloud.google.com/docs)
3. Check [Vertex AI Gemini Docs](https://cloud.google.com/vertex-ai/generative-ai/docs)
4. Contact your GCP account team

---

## ✅ Next Steps

Once setup is complete:

1. ✅ Test with a real RFP document
2. ✅ Customize `config.yaml` for your organization
3. ✅ Set up NotebookLM manually (see output instructions)
4. ✅ Train your team on using the agent
5. ✅ Integrate into your RFP workflow

---

**You're all set! 🎉**

Run `python main.py interactive` to start accelerating your RFP responses!
