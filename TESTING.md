# Testing Guide

## Overview

This guide covers testing strategies for the RFP Accelerator Agent.

## Test Structure

```
tests/
├── unit/                          # Unit tests
│   ├── test_validators.py
│   ├── test_document_parser.py
│   ├── test_workflow_steps.py
│   └── test_integrations.py
├── integration/                   # Integration tests
│   ├── test_google_drive.py
│   ├── test_google_docs.py
│   ├── test_gemini_ai.py
│   └── test_full_workflow.py
└── fixtures/                      # Test data
    ├── sample_rfp.pdf
    ├── sample_rfp.docx
    └── test_config.yaml
```

## Unit Tests

### Testing Validators

```python
# tests/unit/test_validators.py
import pytest
from rfp_agent.utils.validators import (
    validate_email,
    validate_file_path,
    validate_gcp_project_id,
    sanitize_folder_name
)

def test_validate_email():
    assert validate_email("user@example.com") == True
    assert validate_email("invalid.email") == False
    assert validate_email("") == False

def test_validate_gcp_project_id():
    assert validate_gcp_project_id("gcp-sandpit-intelia") == True
    assert validate_gcp_project_id("Invalid_Project") == False
    assert validate_gcp_project_id("a" * 31) == False

def test_sanitize_folder_name():
    result = sanitize_folder_name("Client: Acme Corp / Project")
    assert "/" not in result
    assert ":" not in result
```

### Testing Document Parser

```python
# tests/unit/test_document_parser.py
import pytest
from rfp_agent.utils.document_parser import DocumentParser

def test_parse_pdf(sample_pdf_path):
    result = DocumentParser.parse_document(sample_pdf_path)
    assert 'text' in result
    assert 'metadata' in result
    assert 'file_info' in result
    assert result['file_info']['extension'] == '.pdf'

def test_extract_client_info():
    text = """
    RFP #12345
    Acme Corporation
    Digital Transformation Initiative
    Deadline: December 31, 2024
    """
    info = DocumentParser.extract_client_info(text)
    assert info['rfp_number'] == '12345'
```

### Testing Workflow Steps

```python
# tests/unit/test_workflow_steps.py
import pytest
from unittest.mock import Mock, patch
from rfp_agent.workflow.step1_ingestion import IngestionStep

def test_ingestion_step():
    config = {'drive_parent_folder_id': None}
    logger = Mock()
    
    step = IngestionStep(config, logger)
    
    context = {
        'rfp_files': ['test.pdf'],
        'client_name': 'Test Client',
        'rfp_title': 'Test RFP',
        'date': '2024-01-01'
    }
    
    with patch('rfp_agent.workflow.step1_ingestion.GoogleDriveClient'):
        result = step.execute(context)
        assert result['status'] == 'success'
```

## Integration Tests

### Testing Google Drive Integration

```python
# tests/integration/test_google_drive.py
import pytest
from rfp_agent.integrations.google_drive import GoogleDriveClient

@pytest.mark.integration
def test_create_folder(gcp_credentials):
    client = GoogleDriveClient(credentials_path=gcp_credentials)
    
    result = client.create_project_folder(
        folder_name="Test RFP Project",
        parent_folder_id=None
    )
    
    assert 'main_folder_id' in result
    assert 'main_folder_url' in result
    assert 'subfolders' in result
    
    # Cleanup
    # Delete test folder

@pytest.mark.integration
def test_upload_file(gcp_credentials, test_file_path):
    client = GoogleDriveClient(credentials_path=gcp_credentials)
    
    # Create test folder first
    folder = client._create_folder("Test Upload")
    
    result = client.upload_file(
        file_path=test_file_path,
        folder_id=folder['id']
    )
    
    assert 'id' in result
    assert 'url' in result
    
    # Cleanup
```

### Testing Gemini AI Integration

```python
# tests/integration/test_gemini_ai.py
import pytest
from rfp_agent.integrations.gemini_ai import GeminiClient

@pytest.mark.integration
def test_analyze_rfp_document():
    client = GeminiClient(
        project_id="gcp-sandpit-intelia",
        model_name="gemini-1.5-pro-002"
    )
    
    sample_text = """
    Request for Proposal
    Acme Corporation
    Digital Transformation Initiative
    
    We are seeking proposals for...
    """
    
    result = client.analyze_rfp_document(sample_text)
    
    assert isinstance(result, dict)
    # Check for expected fields

@pytest.mark.integration
def test_generate_questions():
    client = GeminiClient(project_id="gcp-sandpit-intelia")
    
    sample_text = "Sample RFP text..."
    
    questions = client.generate_follow_up_questions(
        document_text=sample_text,
        min_questions=5,
        max_questions=10
    )
    
    assert isinstance(questions, list)
    assert len(questions) >= 5
    assert len(questions) <= 10
```

### Testing Full Workflow

```python
# tests/integration/test_full_workflow.py
import pytest
from rfp_agent import RFPAcceleratorAgent

@pytest.mark.integration
@pytest.mark.slow
def test_complete_workflow(sample_rfp_files, test_config):
    agent = RFPAcceleratorAgent(
        gcp_project="gcp-sandpit-intelia",
        config_path=test_config
    )
    
    result = agent.execute_workflow(
        rfp_files=sample_rfp_files,
        client_name="Test Client",
        rfp_title="Test RFP",
        team_members=["test@example.com"],
        steps_to_run=[1, 2, 3]  # Run first 3 steps only
    )
    
    assert result['status'] == 'success'
    assert 'folder_url' in result['context']
    assert 'questions_doc_url' in result['context']
    
    # Cleanup test resources
```

## Fixtures

```python
# tests/conftest.py
import pytest
from pathlib import Path

@pytest.fixture
def sample_pdf_path():
    return Path(__file__).parent / "fixtures" / "sample_rfp.pdf"

@pytest.fixture
def sample_rfp_files():
    fixtures_dir = Path(__file__).parent / "fixtures"
    return [
        str(fixtures_dir / "sample_rfp.pdf"),
        str(fixtures_dir / "sample_rfp.docx")
    ]

@pytest.fixture
def test_config():
    return Path(__file__).parent / "fixtures" / "test_config.yaml"

@pytest.fixture
def gcp_credentials():
    # Return path to test service account credentials
    return None  # Use application default credentials

@pytest.fixture
def test_file_path(tmp_path):
    # Create a temporary test file
    test_file = tmp_path / "test.txt"
    test_file.write_text("Test content")
    return str(test_file)
```

## Running Tests

### All Tests
```powershell
pytest tests/
```

### Unit Tests Only
```powershell
pytest tests/unit/
```

### Integration Tests Only
```powershell
pytest tests/integration/ -m integration
```

### With Coverage
```powershell
pytest --cov=rfp_agent tests/
```

### Specific Test File
```powershell
pytest tests/unit/test_validators.py
```

### Verbose Output
```powershell
pytest -v tests/
```

## Test Configuration

### pytest.ini
```ini
[pytest]
markers =
    integration: marks tests as integration tests (deselect with '-m "not integration"')
    slow: marks tests as slow (deselect with '-m "not slow"')
    
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*

# Coverage settings
addopts = 
    --strict-markers
    --disable-warnings
```

## Mocking External Services

### Mocking Google APIs

```python
from unittest.mock import Mock, patch

@patch('rfp_agent.integrations.google_drive.build')
def test_with_mocked_drive(mock_build):
    mock_service = Mock()
    mock_build.return_value = mock_service
    
    # Configure mock responses
    mock_service.files().create().execute.return_value = {
        'id': 'test-folder-id',
        'webViewLink': 'https://drive.google.com/test'
    }
    
    # Run test
    client = GoogleDriveClient()
    result = client._create_folder("Test Folder")
    
    assert result['id'] == 'test-folder-id'
```

### Mocking Gemini AI

```python
@patch('rfp_agent.integrations.gemini_ai.GenerativeModel')
def test_with_mocked_gemini(mock_model):
    mock_response = Mock()
    mock_response.text = '{"client_name": "Test Corp"}'
    
    mock_model.return_value.generate_content.return_value = mock_response
    
    client = GeminiClient(project_id="test-project")
    result = client.analyze_rfp_document("test text")
    
    assert result['client_name'] == 'Test Corp'
```

## Manual Testing

### Test Checklist

- [ ] Setup and installation
- [ ] Configuration file creation
- [ ] GCP authentication
- [ ] Document upload (PDF)
- [ ] Document upload (DOCX)
- [ ] Question generation
- [ ] Answer generation
- [ ] Project plan creation
- [ ] Folder sharing
- [ ] Email notifications
- [ ] Error handling
- [ ] Workflow resumption

### Manual Test Script

```powershell
# 1. Setup
.\setup.ps1

# 2. Create test RFP file
# (Use a real or sample RFP document)

# 3. Run workflow
python main.py run `
  -f "test_rfp.pdf" `
  -c "Test Client" `
  -t "Test Project" `
  -m "your-email@example.com"

# 4. Verify outputs
# - Check Google Drive folder created
# - Check documents generated
# - Check email received

# 5. Test error handling
python main.py run `
  -f "nonexistent.pdf" `
  -c "Test" `
  -t "Test"
# Should show clear error message

# 6. Test interactive mode
python main.py interactive
```

## Performance Testing

### Load Testing

```python
import time
from concurrent.futures import ThreadPoolExecutor

def test_concurrent_workflows():
    """Test multiple concurrent workflow executions."""
    
    def run_workflow(i):
        agent = RFPAcceleratorAgent(gcp_project="gcp-sandpit-intelia")
        start = time.time()
        
        result = agent.execute_workflow(
            rfp_files=[f"test_{i}.pdf"],
            client_name=f"Client {i}",
            rfp_title=f"Project {i}"
        )
        
        duration = time.time() - start
        return duration
    
    with ThreadPoolExecutor(max_workers=5) as executor:
        durations = list(executor.map(run_workflow, range(5)))
    
    avg_duration = sum(durations) / len(durations)
    print(f"Average workflow duration: {avg_duration:.2f}s")
```

## Continuous Integration

### GitHub Actions Example

```yaml
# .github/workflows/test.yml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v2
    
    - name: Set up Python
      uses: actions/setup-python@v2
      with:
        python-version: '3.9'
    
    - name: Install dependencies
      run: |
        pip install -r requirements.txt
        pip install pytest pytest-cov
    
    - name: Run unit tests
      run: pytest tests/unit/ --cov=rfp_agent
    
    - name: Upload coverage
      uses: codecov/codecov-action@v2
```

## Best Practices

1. **Isolation**: Each test should be independent
2. **Cleanup**: Always clean up created resources
3. **Mocking**: Mock external services in unit tests
4. **Fixtures**: Use fixtures for common test data
5. **Markers**: Mark integration and slow tests appropriately
6. **Coverage**: Aim for >80% code coverage
7. **Documentation**: Document complex test scenarios

## Debugging Tests

```powershell
# Run with debugger
pytest --pdb tests/

# Show print statements
pytest -s tests/

# Stop on first failure
pytest -x tests/

# Run last failed tests
pytest --lf tests/
```
