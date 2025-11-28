# RFP Accelerator Agent (R.A.A.)

## Overview
The RFP Accelerator Agent is an automated Project Kickoff Manager that transforms raw Request for Proposal (RFP) documents into fully organized, team-ready, and actionable project workspaces.

## Target Platform
- **GCP Project**: `gcp-sandpit-intelia`
- **Platform**: Gemini Enterprise
- **Framework**: Orchestrated via Antigravity Framework

## Features

### 7-Step Orchestration Workflow

1. **Ingestion & Setup** - Creates project folder structure and uploads RFP documents
2. **Knowledge Base Creation** - Initializes NotebookLM with RFP sources
3. **Question Generation** - Identifies critical ambiguities and missing data points
4. **Draft Answer Generation** - Creates boilerplate responses using internal knowledge
5. **Initial Project Plan** - Extracts deadlines and creates preliminary WBS
6. **Collaboration Prompt** - Collects team member information
7. **Distribution & Launch** - Shares resources and notifies team

## Security & Compliance

- **Data Isolation**: Strict separation between client projects
- **Access Control**: Role-based permissions via Google Workspace
- **Secure Execution**: All operations within Antigravity framework context
- **Audit Trail**: Complete logging of all agent actions

## Prerequisites

### Required APIs
- Google Drive API
- NotebookLM API
- Google Docs API
- Google Workspace API (Gmail)
- Vertex AI (Gemini)

### Service Account Permissions
The service account must have the following roles:
- `roles/drive.file` - Create and manage Drive files
- `roles/docs.editor` - Create and edit Google Docs
- `roles/gmail.send` - Send notification emails
- `roles/aiplatform.user` - Access Vertex AI/Gemini

## Installation

### 1. Set Up Virtual Environment
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Configure GCP Credentials
```bash
# Set your GCP project
gcloud config set project gcp-sandpit-intelia

# Authenticate
gcloud auth application-default login

# Or use service account
export GOOGLE_APPLICATION_CREDENTIALS="path/to/service-account-key.json"
```

### 3. Enable Required APIs
```bash
gcloud services enable drive.googleapis.com
gcloud services enable docs.googleapis.com
gcloud services enable gmail.googleapis.com
gcloud services enable aiplatform.googleapis.com
```

### 4. Configure Settings
Copy `config.example.yaml` to `config.yaml` and update with your settings:
```yaml
gcp_project: gcp-sandpit-intelia
gemini_model: gemini-1.5-pro-002
drive_parent_folder_id: "your-parent-folder-id"
internal_knowledge_source: "path/to/company-knowledge-base"
```

## Usage

### Basic Usage
```python
from rfp_agent import RFPAcceleratorAgent

# Initialize the agent
agent = RFPAcceleratorAgent(
    gcp_project="gcp-sandpit-intelia",
    config_path="config.yaml"
)

# Run the complete workflow
result = agent.execute_workflow(
    rfp_files=["path/to/rfp1.pdf", "path/to/rfp2.docx"],
    client_name="Acme Corporation",
    rfp_title="Digital Transformation Initiative"
)

# Access results
print(f"Project Folder: {result['folder_url']}")
print(f"NotebookLM: {result['notebook_url']}")
print(f"Questions Doc: {result['questions_doc_url']}")
```

### Command Line Interface
```bash
# Run the full workflow
python main.py --rfp-files rfp1.pdf rfp2.docx --client "Acme Corp" --title "Digital Transformation"

# Run specific steps only
python main.py --rfp-files rfp1.pdf --steps 1,2,3

# Interactive mode
python main.py --interactive
```

## Architecture

```
rfp-agent/
├── main.py                 # CLI entry point
├── rfp_agent/
│   ├── __init__.py
│   ├── agent.py           # Main orchestrator
│   ├── workflow/
│   │   ├── __init__.py
│   │   ├── step1_ingestion.py
│   │   ├── step2_knowledge_base.py
│   │   ├── step3_questions.py
│   │   ├── step4_answers.py
│   │   ├── step5_project_plan.py
│   │   ├── step6_collaboration.py
│   │   └── step7_distribution.py
│   ├── integrations/
│   │   ├── __init__.py
│   │   ├── google_drive.py
│   │   ├── notebooklm.py
│   │   ├── google_docs.py
│   │   ├── google_workspace.py
│   │   └── gemini_ai.py
│   └── utils/
│       ├── __init__.py
│       ├── document_parser.py
│       ├── logger.py
│       └── validators.py
├── config.yaml
├── requirements.txt
└── README.md
```

## Output Structure

For each RFP, the agent creates:

```
[Client Name] - [RFP Title] - [Date]/
├── 00_Source_Documents/
│   ├── original_rfp.pdf
│   └── attachments/
├── 01_Analysis/
│   ├── Client_Follow-up_Questions.gdoc
│   └── Draft_RFP_Answers.gdoc
├── 02_Planning/
│   └── Draft_Project_Plan.gdoc
└── 03_Collaboration/
    └── NotebookLM (link)
```

## Workflow Details

### Step 1: Ingestion & Setup
- Extracts client name and RFP title from documents
- Creates structured folder hierarchy in Google Drive
- Uploads all source documents
- Returns folder ID and URL

### Step 2: Knowledge Base Creation
- Creates NotebookLM notebook with project name
- Adds all RFP documents as sources
- Verifies successful indexing
- Returns notebook URL

### Step 3: Question Generation
- Analyzes RFP for ambiguities and gaps
- Identifies 10-15 critical questions
- Creates structured Google Doc
- Categorizes questions by priority

### Step 4: Draft Answer Generation
- Extracts explicit RFP questions
- Generates draft responses using internal knowledge
- Creates formatted Google Doc
- Includes placeholders for customization

### Step 5: Initial Project Plan
- Extracts deadlines and milestones
- Creates preliminary WBS
- Estimates resource allocation
- Generates Gantt chart (optional)

### Step 6: Collaboration Prompt
- Prompts user for team member emails
- Validates email addresses
- Logs team members for access control

### Step 7: Distribution & Launch
- Shares folder with team members
- Shares NotebookLM notebook
- Sends notification email with:
  - Project summary
  - Links to all resources
  - Next steps

## Error Handling

The agent includes comprehensive error handling:
- API rate limiting and retry logic
- Document parsing failures
- Invalid team member emails
- Insufficient permissions
- Network timeouts

## Logging & Monitoring

All operations are logged with:
- Timestamp
- Step number and name
- Action taken
- Success/failure status
- Error details (if applicable)

Logs are stored in:
- Console output (INFO level)
- `logs/rfp_agent.log` (DEBUG level)
- Cloud Logging (production)

## Testing

```bash
# Run unit tests
pytest tests/unit/

# Run integration tests (requires GCP access)
pytest tests/integration/

# Run with coverage
pytest --cov=rfp_agent tests/
```

## Troubleshooting

### Common Issues

**Issue**: "Permission denied" errors
**Solution**: Verify service account has required roles and APIs are enabled

**Issue**: NotebookLM creation fails
**Solution**: Ensure NotebookLM API is available in your region

**Issue**: Email notifications not sent
**Solution**: Check Gmail API is enabled and sender email is verified

## Contributing

This is an internal tool for the Antigravity framework. For issues or enhancements, contact the development team.

## License

Proprietary - Internal Use Only

## Support

For support, contact: [Your Support Channel]
