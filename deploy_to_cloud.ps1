
# Deploy to Google Cloud Run
Write-Host "Deploying RFP Accelerator Agent to Cloud Run..." -ForegroundColor Cyan

# 1. Enable Cloud Build and Cloud Run APIs
Write-Host "Enabling Cloud Build and Cloud Run APIs..."
gcloud services enable cloudbuild.googleapis.com run.googleapis.com

# 2. Submit build and deploy
Write-Host "Building and Deploying..."
gcloud run deploy rfp-agent-service `
    --source . `
    --region us-central1 `
    --project gcp-sandpit-intelia `
    --allow-unauthenticated `
    --set-env-vars "GCP_PROJECT=gcp-sandpit-intelia"

Write-Host "Deployment Complete!" -ForegroundColor Green
