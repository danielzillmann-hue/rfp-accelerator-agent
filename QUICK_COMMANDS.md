# Quick Setup Commands - RFP Accelerator Agent
## Copy and paste these commands to get started quickly

## 1️⃣ Configure gcloud
gcloud config set project gcp-sandpit-intelia
gcloud auth login
gcloud auth application-default login

## 2️⃣ Enable APIs (all at once)
gcloud services enable drive.googleapis.com docs.googleapis.com gmail.googleapis.com aiplatform.googleapis.com logging.googleapis.com

## 3️⃣ Create Service Account (Optional - for production)
gcloud iam service-accounts create rfp-accelerator-agent --display-name="RFP Accelerator Agent"

## 4️⃣ Grant IAM Roles (if using service account)
$SA_EMAIL = "rfp-accelerator-agent@gcp-sandpit-intelia.iam.gserviceaccount.com"
gcloud projects add-iam-policy-binding gcp-sandpit-intelia --member="serviceAccount:$SA_EMAIL" --role="roles/aiplatform.user"
gcloud projects add-iam-policy-binding gcp-sandpit-intelia --member="serviceAccount:$SA_EMAIL" --role="roles/logging.logWriter"

## 5️⃣ Create Service Account Key (if using service account)
New-Item -ItemType Directory -Path ".\credentials" -Force
gcloud iam service-accounts keys create credentials\rfp-agent-key.json --iam-account=rfp-accelerator-agent@gcp-sandpit-intelia.iam.gserviceaccount.com

## 6️⃣ Install Python Dependencies
.\setup.ps1
# OR manually:
python -m venv venv
.\venv\Scripts\Activate
pip install -r requirements.txt

## 7️⃣ Configure Application
Copy-Item config.example.yaml config.yaml
notepad config.yaml
# Update: gcp_project, email_sender, company_info

## 8️⃣ Test Installation
python -c "from rfp_agent import RFPAcceleratorAgent; print('✓ Success')"
python main.py status

## 9️⃣ Run Your First RFP
python main.py interactive
# OR
python main.py run -f "your_rfp.pdf" -c "Client Name" -t "RFP Title" -m "your-email@domain.com"

## 🔍 Verification Commands
# Check enabled APIs
gcloud services list --enabled | Select-String -Pattern "drive|docs|gmail|aiplatform"

# Check Gemini access
gcloud ai models list --region=us-central1 --project=gcp-sandpit-intelia

# Check service accounts
gcloud iam service-accounts list

# View recent logs
gcloud logging read "resource.type=global" --limit=10

## 🐛 Troubleshooting Commands
# Re-authenticate
gcloud auth application-default login

# Check current project
gcloud config get-value project

# Test Vertex AI connection
python -c "from google.cloud import aiplatform; aiplatform.init(project='gcp-sandpit-intelia', location='us-central1'); print('✓ Connected')"

# Test Gemini model
python -c "from vertexai.generative_models import GenerativeModel; model = GenerativeModel('gemini-1.5-pro-002'); print('✓ Gemini accessible')"

## 📝 Notes
# - For development: Use user credentials (gcloud auth application-default login)
# - For production: Use service account with domain-wide delegation
# - Keep credentials/ folder secure (already in .gitignore)
# - Update config.yaml with your organization details
