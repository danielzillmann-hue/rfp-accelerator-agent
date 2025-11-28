# Quick Start Guide

## Installation

1. **Clone or download the project**

2. **Create virtual environment**
```powershell
python -m venv venv
.\venv\Scripts\activate
```

3. **Install dependencies**
```powershell
pip install -r requirements.txt
```

4. **Configure GCP credentials**
```powershell
# Set your GCP project
gcloud config set project gcp-sandpit-intelia

# Authenticate
gcloud auth application-default login
```

5. **Create configuration file**
```powershell
copy config.example.yaml config.yaml
# Edit config.yaml with your settings
```

## Basic Usage

### Command Line

```powershell
# Run complete workflow
python main.py run `
  -f "path\to\rfp.pdf" `
  -c "Acme Corporation" `
  -t "Digital Transformation" `
  -m "pm@company.com" `
  -m "analyst@company.com"

# Interactive mode
python main.py interactive

# Check status
python main.py status
```

### Python API

```python
from rfp_agent import RFPAcceleratorAgent

agent = RFPAcceleratorAgent(
    gcp_project="gcp-sandpit-intelia",
    config_path="config.yaml"
)

result = agent.execute_workflow(
    rfp_files=["rfp.pdf"],
    client_name="Acme Corp",
    rfp_title="Digital Transformation",
    team_members=["pm@company.com"]
)

print(result['context']['folder_url'])
```

## What Gets Created

For each RFP, the agent creates:

1. **Google Drive Folder Structure**
   - Main project folder
   - Source documents subfolder
   - Analysis subfolder
   - Planning subfolder
   - Collaboration subfolder

2. **Google Docs**
   - Follow-up Questions document
   - Draft RFP Answers document
   - Draft Project Plan document

3. **NotebookLM Notebook** (manual setup required)
   - Knowledge base with all RFP sources

4. **Email Notifications**
   - Sent to all team members
   - Contains links to all resources

## Next Steps

1. Review the generated follow-up questions
2. Customize the draft answers
3. Refine the project plan
4. Set up NotebookLM manually (see instructions in output)
5. Schedule kickoff meeting with team

## Troubleshooting

**Issue**: Permission denied errors
**Solution**: Ensure service account has required roles

**Issue**: NotebookLM not created
**Solution**: NotebookLM API not available - follow manual setup instructions

**Issue**: Emails not sent
**Solution**: Check Gmail API is enabled and sender email is configured

## Support

For issues or questions, refer to the main README.md or contact your administrator.
