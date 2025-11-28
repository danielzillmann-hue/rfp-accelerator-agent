# Architecture & Design

## System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                     RFP Accelerator Agent                        │
│                  (Antigravity Framework)                         │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                      Main Orchestrator                           │
│                    (agent.py)                                    │
│  • Workflow coordination                                         │
│  • State management                                              │
│  • Error handling                                                │
└─────────────────────────────────────────────────────────────────┘
                              │
        ┌─────────────────────┼─────────────────────┐
        ▼                     ▼                     ▼
┌──────────────┐    ┌──────────────┐      ┌──────────────┐
│   Workflow   │    │ Integrations │      │  Utilities   │
│    Steps     │    │              │      │              │
└──────────────┘    └──────────────┘      └──────────────┘
        │                   │                      │
        ▼                   ▼                      ▼
┌──────────────┐    ┌──────────────┐      ┌──────────────┐
│ Step 1-7     │    │ Google APIs  │      │ Validators   │
│ Execution    │    │ • Drive      │      │ • Email      │
│              │    │ • Docs       │      │ • Files      │
│              │    │ • Workspace  │      │ • Sanitize   │
│              │    │ • Gemini AI  │      │              │
│              │    │ • NotebookLM │      │ Parsers      │
│              │    │              │      │ • PDF        │
│              │    │              │      │ • DOCX       │
│              │    │              │      │ • TXT        │
│              │    │              │      │              │
│              │    │              │      │ Logger       │
│              │    │              │      │ • Structured │
│              │    │              │      │ • JSON       │
└──────────────┘    └──────────────┘      └──────────────┘
        │                   │                      │
        └───────────────────┴──────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────────┐
│                   Google Cloud Platform                          │
│                  (gcp-sandpit-intelia)                           │
│                                                                   │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐          │
│  │ Google Drive │  │ Google Docs  │  │  Vertex AI   │          │
│  │              │  │              │  │  (Gemini)    │          │
│  │ • Folders    │  │ • Questions  │  │              │          │
│  │ • Files      │  │ • Answers    │  │ • Analysis   │          │
│  │ • Sharing    │  │ • Plans      │  │ • Generation │          │
│  └──────────────┘  └──────────────┘  └──────────────┘          │
│                                                                   │
│  ┌──────────────┐  ┌──────────────┐                             │
│  │   Gmail API  │  │  NotebookLM  │                             │
│  │              │  │  (Manual)    │                             │
│  │ • Notify     │  │              │                             │
│  │ • Invite     │  │ • Knowledge  │                             │
│  └──────────────┘  └──────────────┘                             │
└─────────────────────────────────────────────────────────────────┘
```

## Workflow Sequence

```
User Input
    │
    ▼
┌────────────────────────────────────────┐
│ Step 1: Ingestion & Setup              │
│ • Parse RFP documents                  │
│ • Extract client info                  │
│ • Create folder structure              │
│ • Upload source files                  │
└────────────────────────────────────────┘
    │
    ▼
┌────────────────────────────────────────┐
│ Step 2: Knowledge Base Creation        │
│ • Create NotebookLM notebook           │
│ • Add RFP sources                      │
│ • Verify indexing                      │
└────────────────────────────────────────┘
    │
    ▼
┌────────────────────────────────────────┐
│ Step 3: Question Generation            │
│ • Analyze RFP with Gemini              │
│ • Identify ambiguities                 │
│ • Generate 10-15 questions             │
│ • Create Questions document            │
└────────────────────────────────────────┘
    │
    ▼
┌────────────────────────────────────────┐
│ Step 4: Draft Answer Generation        │
│ • Extract RFP questions                │
│ • Load internal knowledge              │
│ • Generate draft responses             │
│ • Create Answers document              │
└────────────────────────────────────────┘
    │
    ▼
┌────────────────────────────────────────┐
│ Step 5: Initial Project Plan           │
│ • Extract timeline data                │
│ • Identify milestones                  │
│ • Create WBS structure                 │
│ • Generate Plan document               │
└────────────────────────────────────────┘
    │
    ▼
┌────────────────────────────────────────┐
│ Step 6: Collaboration Prompt           │
│ • Collect team emails                  │
│ • Validate addresses                   │
│ • Log team members                     │
└────────────────────────────────────────┘
    │
    ▼
┌────────────────────────────────────────┐
│ Step 7: Distribution & Launch          │
│ • Share Drive folder                   │
│ • Share NotebookLM                     │
│ • Send notification emails             │
│ • Provide resource links               │
└────────────────────────────────────────┘
    │
    ▼
Complete Project Workspace
```

## Data Flow

```
RFP Documents (PDF, DOCX, etc.)
    │
    ▼
Document Parser
    │
    ├─► Text Extraction
    ├─► Metadata Extraction
    └─► Client Info Extraction
    │
    ▼
Gemini AI Analysis
    │
    ├─► Question Generation
    ├─► Answer Generation
    └─► Timeline Extraction
    │
    ▼
Google Docs Creation
    │
    ├─► Questions Document
    ├─► Answers Document
    └─► Project Plan Document
    │
    ▼
Google Drive Organization
    │
    └─► Structured Folder Hierarchy
    │
    ▼
Team Distribution
    │
    ├─► Folder Sharing
    ├─► NotebookLM Sharing
    └─► Email Notifications
```

## Security Model

```
┌─────────────────────────────────────────┐
│         Service Account                 │
│    (gcp-sandpit-intelia)                │
└─────────────────────────────────────────┘
    │
    ├─► roles/drive.file
    ├─► roles/docs.editor
    ├─► roles/gmail.send
    └─► roles/aiplatform.user
    │
    ▼
┌─────────────────────────────────────────┐
│      Data Isolation Layer               │
│  • Project-specific folders             │
│  • Access control per project           │
│  • Audit logging enabled                │
└─────────────────────────────────────────┘
    │
    ▼
┌─────────────────────────────────────────┐
│      Team Member Access                 │
│  • Email-based permissions              │
│  • Configurable roles (reader/writer)   │
│  • Notification on share                │
└─────────────────────────────────────────┘
```

## Component Responsibilities

### Main Orchestrator (`agent.py`)
- Workflow state management
- Step coordination
- Error handling and recovery
- Configuration management
- Status reporting

### Workflow Steps (`workflow/`)
- Step 1: File system operations, document parsing
- Step 2: Knowledge base initialization
- Step 3: AI-powered question generation
- Step 4: AI-powered answer drafting
- Step 5: Timeline extraction and planning
- Step 6: Team member validation
- Step 7: Resource sharing and notifications

### Integrations (`integrations/`)
- **Google Drive**: Folder creation, file uploads, sharing
- **Google Docs**: Document creation, content formatting
- **Google Workspace**: Email composition and sending
- **Gemini AI**: Document analysis, content generation
- **NotebookLM**: Knowledge base management (placeholder)

### Utilities (`utils/`)
- **Validators**: Email, file path, GCP project ID validation
- **Document Parser**: Multi-format document text extraction
- **Logger**: Structured logging with JSON support

## Error Handling Strategy

```
┌─────────────────────────────────────────┐
│         Error Detection                 │
│  • API failures                         │
│  • Invalid inputs                       │
│  • Permission errors                    │
│  • Network timeouts                     │
└─────────────────────────────────────────┘
    │
    ▼
┌─────────────────────────────────────────┐
│         Error Classification            │
│  • Recoverable (retry)                  │
│  • User error (validation)              │
│  • System error (abort)                 │
└─────────────────────────────────────────┘
    │
    ▼
┌─────────────────────────────────────────┐
│         Error Response                  │
│  • Log error details                    │
│  • Update workflow state                │
│  • Provide user feedback                │
│  • Enable workflow resume               │
└─────────────────────────────────────────┘
```

## Configuration Hierarchy

```
Default Config (hardcoded)
    │
    ▼
config.example.yaml (template)
    │
    ▼
config.yaml (user customized)
    │
    ▼
CLI Arguments (runtime override)
    │
    ▼
Final Configuration
```

## Extensibility Points

1. **Custom Workflow Steps**: Inherit from `WorkflowStep` base class
2. **Additional Integrations**: Add new clients in `integrations/`
3. **Document Formats**: Extend `DocumentParser` with new parsers
4. **Validation Rules**: Add validators in `utils/validators.py`
5. **AI Models**: Configure different Gemini models in config
6. **Output Formats**: Customize document templates in integrations

## Performance Considerations

- **Parallel Processing**: Independent API calls can run concurrently
- **Caching**: Document parsing results cached during workflow
- **Batch Operations**: Multiple file uploads batched when possible
- **Retry Logic**: Exponential backoff for API rate limits
- **Streaming**: Large documents processed in chunks

## Monitoring & Observability

- **Structured Logging**: JSON format for easy parsing
- **Cloud Logging**: Integration with GCP Cloud Logging
- **Progress Tracking**: Real-time workflow progress updates
- **Audit Trail**: Complete record of all operations
- **Error Reporting**: Detailed error context and stack traces
