
# GitHub Deployment Instructions

Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "       GITHUB DEPLOYMENT SETUP" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""

Write-Host "STEP 1: Create Repository" -ForegroundColor Yellow
Write-Host "1. Go to https://github.com/new"
Write-Host "2. Create a repository named 'rfp-accelerator-agent'"
Write-Host "3. Do NOT initialize with README, .gitignore, or License"
Write-Host ""

Write-Host "STEP 2: Push Code" -ForegroundColor Yellow
Write-Host "Run these commands in your terminal:"
Write-Host "git remote add origin https://github.com/[YOUR_USERNAME]/rfp-accelerator-agent.git" -ForegroundColor White
Write-Host "git branch -M main" -ForegroundColor White
Write-Host "git push -u origin main" -ForegroundColor White
Write-Host ""

Write-Host "STEP 3: Configure Secrets" -ForegroundColor Yellow
Write-Host "1. Go to your new repo > Settings > Secrets and variables > Actions"
Write-Host "2. Click 'New repository secret'"
Write-Host "3. Name: GCP_SA_KEY"
Write-Host "4. Value: Paste the content of credentials/rfp-agent-key.json"
Write-Host ""
Write-Host "(Note: If you haven't created the key yet, run the command below)"
Write-Host "gcloud iam service-accounts keys create credentials/rfp-agent-key.json --iam-account=rfp-accelerator-agent@gcp-sandpit-intelia.iam.gserviceaccount.com" -ForegroundColor Gray
Write-Host ""

Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "Once you push, go to the 'Actions' tab in GitHub to watch your deployment!" -ForegroundColor Green
