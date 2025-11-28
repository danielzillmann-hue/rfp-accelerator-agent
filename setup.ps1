# RFP Accelerator Agent - Setup Script
# Run this script to set up the project

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "RFP Accelerator Agent - Setup" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Check Python installation
Write-Host "Checking Python installation..." -ForegroundColor Yellow
$pythonVersion = python --version 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Host "ERROR: Python is not installed or not in PATH" -ForegroundColor Red
    exit 1
}
Write-Host "✓ Found: $pythonVersion" -ForegroundColor Green
Write-Host ""

# Check gcloud installation
Write-Host "Checking gcloud installation..." -ForegroundColor Yellow
$gcloudVersion = gcloud version 2>&1 | Select-String "Google Cloud SDK"
if ($LASTEXITCODE -ne 0) {
    Write-Host "WARNING: gcloud CLI not found. You'll need it for GCP authentication." -ForegroundColor Yellow
} else {
    Write-Host "✓ Found: $gcloudVersion" -ForegroundColor Green
}
Write-Host ""

# Create virtual environment
Write-Host "Creating virtual environment..." -ForegroundColor Yellow
if (Test-Path "venv") {
    Write-Host "Virtual environment already exists" -ForegroundColor Yellow
} else {
    python -m venv venv
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✓ Virtual environment created" -ForegroundColor Green
    } else {
        Write-Host "ERROR: Failed to create virtual environment" -ForegroundColor Red
        exit 1
    }
}
Write-Host ""

# Activate virtual environment
Write-Host "Activating virtual environment..." -ForegroundColor Yellow
& ".\venv\Scripts\Activate.ps1"
Write-Host "✓ Virtual environment activated" -ForegroundColor Green
Write-Host ""

# Upgrade pip
Write-Host "Upgrading pip..." -ForegroundColor Yellow
python -m pip install --upgrade pip --quiet
Write-Host "✓ pip upgraded" -ForegroundColor Green
Write-Host ""

# Install dependencies
Write-Host "Installing dependencies..." -ForegroundColor Yellow
pip install -r requirements.txt --quiet
if ($LASTEXITCODE -eq 0) {
    Write-Host "✓ Dependencies installed" -ForegroundColor Green
} else {
    Write-Host "ERROR: Failed to install dependencies" -ForegroundColor Red
    exit 1
}
Write-Host ""

# Create logs directory
Write-Host "Creating logs directory..." -ForegroundColor Yellow
if (-not (Test-Path "logs")) {
    New-Item -ItemType Directory -Path "logs" | Out-Null
    Write-Host "✓ Logs directory created" -ForegroundColor Green
} else {
    Write-Host "Logs directory already exists" -ForegroundColor Yellow
}
Write-Host ""

# Create config file if it doesn't exist
Write-Host "Checking configuration..." -ForegroundColor Yellow
if (-not (Test-Path "config.yaml")) {
    Copy-Item "config.example.yaml" "config.yaml"
    Write-Host "✓ Created config.yaml from template" -ForegroundColor Green
    Write-Host "  Please edit config.yaml with your settings" -ForegroundColor Yellow
} else {
    Write-Host "config.yaml already exists" -ForegroundColor Yellow
}
Write-Host ""

# GCP Setup Instructions
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "GCP Setup Required" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "1. Set your GCP project:" -ForegroundColor Yellow
Write-Host "   gcloud config set project gcp-sandpit-intelia" -ForegroundColor White
Write-Host ""
Write-Host "2. Authenticate:" -ForegroundColor Yellow
Write-Host "   gcloud auth application-default login" -ForegroundColor White
Write-Host ""
Write-Host "3. Enable required APIs:" -ForegroundColor Yellow
Write-Host "   gcloud services enable drive.googleapis.com" -ForegroundColor White
Write-Host "   gcloud services enable docs.googleapis.com" -ForegroundColor White
Write-Host "   gcloud services enable gmail.googleapis.com" -ForegroundColor White
Write-Host "   gcloud services enable aiplatform.googleapis.com" -ForegroundColor White
Write-Host ""
Write-Host "4. Edit config.yaml with your settings" -ForegroundColor Yellow
Write-Host ""

# Test installation
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Testing Installation" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Running basic import test..." -ForegroundColor Yellow

$testScript = @"
try:
    from rfp_agent import RFPAcceleratorAgent
    print('✓ RFP Agent module imported successfully')
    exit(0)
except Exception as e:
    print(f'✗ Import failed: {e}')
    exit(1)
"@

$testScript | python -
if ($LASTEXITCODE -eq 0) {
    Write-Host "✓ Installation test passed" -ForegroundColor Green
} else {
    Write-Host "✗ Installation test failed" -ForegroundColor Red
}
Write-Host ""

# Final message
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Setup Complete!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Yellow
Write-Host "1. Complete GCP setup (see instructions above)" -ForegroundColor White
Write-Host "2. Edit config.yaml with your settings" -ForegroundColor White
Write-Host "3. Run: python main.py --help" -ForegroundColor White
Write-Host "4. Or run: python main.py interactive" -ForegroundColor White
Write-Host ""
Write-Host "For more information, see README.md and QUICKSTART.md" -ForegroundColor Cyan
Write-Host ""
