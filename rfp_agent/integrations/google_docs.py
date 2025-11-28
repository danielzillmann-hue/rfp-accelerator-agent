"""
Google Docs API client for creating and managing documents.
"""

from typing import Dict, List, Optional, Any

from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import structlog


class GoogleDocsClient:
    """
    Client for interacting with Google Docs API.
    """
    
    def __init__(self, credentials_path: Optional[str] = None, logger: Optional[structlog.BoundLogger] = None):
        """
        Initialize Google Docs client.
        
        Args:
            credentials_path: Path to service account credentials JSON
            logger: Optional logger instance
        """
        self.logger = logger or structlog.get_logger(__name__)
        
        # Initialize credentials
        if credentials_path:
            credentials = service_account.Credentials.from_service_account_file(
                credentials_path,
                scopes=['https://www.googleapis.com/auth/documents', 'https://www.googleapis.com/auth/drive']
            )
        else:
            from google.auth import default
            credentials, _ = default(scopes=['https://www.googleapis.com/auth/documents', 'https://www.googleapis.com/auth/drive'])
        
        # Build the Docs and Drive services
        self.docs_service = build('docs', 'v1', credentials=credentials)
        self.drive_service = build('drive', 'v3', credentials=credentials)
        self.logger.info("Google Docs client initialized")
    
    def create_document(
        self,
        title: str,
        folder_id: Optional[str] = None
    ) -> Dict[str, str]:
        """
        Create a new Google Doc.
        
        Args:
            title: Document title
            folder_id: Optional folder ID to create document in
        
        Returns:
            Dictionary with document ID and URL
        """
        try:
            # Create the document
            doc = self.docs_service.documents().create(
                body={'title': title}
            ).execute()
            
            doc_id = doc['documentId']
            
            # Move to folder if specified
            if folder_id:
                self.drive_service.files().update(
                    fileId=doc_id,
                    addParents=folder_id,
                    removeParents='root',
                    fields='id, parents'
                ).execute()
            
            # Get the web view link
            file = self.drive_service.files().get(
                fileId=doc_id,
                fields='webViewLink'
            ).execute()
            
            self.logger.info(f"Created document: {title}", doc_id=doc_id)
            
            return {
                'id': doc_id,
                'url': file['webViewLink']
            }
            
        except HttpError as e:
            self.logger.error(f"Failed to create document: {e}")
            raise
    
    def write_content(
        self,
        doc_id: str,
        content: List[Dict[str, Any]],
        append: bool = True
    ) -> bool:
        """
        Write structured content to a Google Doc.
        
        Args:
            doc_id: Document ID
            content: List of content blocks with type and text
            append: Whether to append or replace content
        
        Returns:
            True if successful
        """
        try:
            requests = []
            
            # If not appending, delete existing content first
            if not append:
                doc = self.docs_service.documents().get(documentId=doc_id).execute()
                end_index = doc['body']['content'][-1]['endIndex']
                
                requests.append({
                    'deleteContentRange': {
                        'range': {
                            'startIndex': 1,
                            'endIndex': end_index - 1
                        }
                    }
                })
            
            # Build insert requests for each content block
            index = 1
            for block in content:
                block_type = block.get('type', 'paragraph')
                text = block.get('text', '')
                
                if block_type == 'heading1':
                    requests.extend(self._create_heading_requests(text, index, 'HEADING_1'))
                    index += len(text) + 1
                elif block_type == 'heading2':
                    requests.extend(self._create_heading_requests(text, index, 'HEADING_2'))
                    index += len(text) + 1
                elif block_type == 'heading3':
                    requests.extend(self._create_heading_requests(text, index, 'HEADING_3'))
                    index += len(text) + 1
                elif block_type == 'bullet':
                    requests.extend(self._create_bullet_requests(text, index))
                    index += len(text) + 1
                elif block_type == 'numbered':
                    requests.extend(self._create_numbered_requests(text, index))
                    index += len(text) + 1
                else:  # paragraph
                    requests.append({
                        'insertText': {
                            'location': {'index': index},
                            'text': text + '\n'
                        }
                    })
                    index += len(text) + 1
            
            # Execute all requests
            if requests:
                self.docs_service.documents().batchUpdate(
                    documentId=doc_id,
                    body={'requests': requests}
                ).execute()
            
            self.logger.info(f"Wrote content to document", doc_id=doc_id, blocks=len(content))
            return True
            
        except HttpError as e:
            self.logger.error(f"Failed to write content: {e}")
            raise
    
    def _create_heading_requests(self, text: str, index: int, style: str) -> List[Dict]:
        """Create requests for a heading."""
        return [
            {
                'insertText': {
                    'location': {'index': index},
                    'text': text + '\n'
                }
            },
            {
                'updateParagraphStyle': {
                    'range': {
                        'startIndex': index,
                        'endIndex': index + len(text) + 1
                    },
                    'paragraphStyle': {
                        'namedStyleType': style
                    },
                    'fields': 'namedStyleType'
                }
            }
        ]
    
    def _create_bullet_requests(self, text: str, index: int) -> List[Dict]:
        """Create requests for a bulleted list item."""
        return [
            {
                'insertText': {
                    'location': {'index': index},
                    'text': text + '\n'
                }
            },
            {
                'createParagraphBullets': {
                    'range': {
                        'startIndex': index,
                        'endIndex': index + len(text) + 1
                    },
                    'bulletPreset': 'BULLET_DISC_CIRCLE_SQUARE'
                }
            }
        ]
    
    def _create_numbered_requests(self, text: str, index: int) -> List[Dict]:
        """Create requests for a numbered list item."""
        return [
            {
                'insertText': {
                    'location': {'index': index},
                    'text': text + '\n'
                }
            },
            {
                'createParagraphBullets': {
                    'range': {
                        'startIndex': index,
                        'endIndex': index + len(text) + 1
                    },
                    'bulletPreset': 'NUMBERED_DECIMAL_ALPHA_ROMAN'
                }
            }
        ]
    
    def create_questions_document(
        self,
        doc_id: str,
        questions: List[Dict[str, str]],
        client_name: str,
        rfp_title: str
    ) -> bool:
        """
        Create a formatted questions document.
        
        Args:
            doc_id: Document ID
            questions: List of question dictionaries with 'category' and 'question'
            client_name: Client name
            rfp_title: RFP title
        
        Returns:
            True if successful
        """
        content = [
            {'type': 'heading1', 'text': f'Follow-up Questions: {client_name}'},
            {'type': 'heading2', 'text': rfp_title},
            {'type': 'paragraph', 'text': ''},
            {'type': 'paragraph', 'text': 'The following questions have been identified to clarify requirements and ensure a comprehensive proposal response:'},
            {'type': 'paragraph', 'text': ''},
        ]
        
        # Group questions by category
        categories = {}
        for q in questions:
            category = q.get('category', 'General')
            if category not in categories:
                categories[category] = []
            categories[category].append(q['question'])
        
        # Add questions by category
        for category, category_questions in categories.items():
            content.append({'type': 'heading3', 'text': category})
            for question in category_questions:
                content.append({'type': 'bullet', 'text': question})
            content.append({'type': 'paragraph', 'text': ''})
        
        return self.write_content(doc_id, content, append=False)
    
    def create_answers_document(
        self,
        doc_id: str,
        answers: List[Dict[str, str]],
        client_name: str,
        rfp_title: str
    ) -> bool:
        """
        Create a formatted draft answers document.
        
        Args:
            doc_id: Document ID
            answers: List of answer dictionaries with 'question' and 'answer'
            client_name: Client name
            rfp_title: RFP title
        
        Returns:
            True if successful
        """
        content = [
            {'type': 'heading1', 'text': f'Draft RFP Responses: {client_name}'},
            {'type': 'heading2', 'text': rfp_title},
            {'type': 'paragraph', 'text': ''},
            {'type': 'paragraph', 'text': 'Note: These are draft responses based on standard templates. Please review and customize as needed.'},
            {'type': 'paragraph', 'text': ''},
        ]
        
        for i, answer_block in enumerate(answers, 1):
            content.append({'type': 'heading3', 'text': f'Question {i}: {answer_block["question"]}'})
            content.append({'type': 'paragraph', 'text': answer_block['answer']})
            content.append({'type': 'paragraph', 'text': ''})
        
        return self.write_content(doc_id, content, append=False)
    
    def create_project_plan_document(
        self,
        doc_id: str,
        plan_data: Dict[str, Any],
        client_name: str,
        rfp_title: str
    ) -> bool:
        """
        Create a formatted project plan document.
        
        Args:
            doc_id: Document ID
            plan_data: Dictionary with milestones, deliverables, timeline
            client_name: Client name
            rfp_title: RFP title
        
        Returns:
            True if successful
        """
        content = [
            {'type': 'heading1', 'text': f'Draft Project Plan: {client_name}'},
            {'type': 'heading2', 'text': rfp_title},
            {'type': 'paragraph', 'text': ''},
        ]
        
        # Add timeline section
        if 'timeline' in plan_data:
            content.append({'type': 'heading3', 'text': 'Project Timeline'})
            for milestone in plan_data['timeline']:
                content.append({'type': 'bullet', 'text': f"{milestone['name']}: {milestone['date']}"})
            content.append({'type': 'paragraph', 'text': ''})
        
        # Add deliverables section
        if 'deliverables' in plan_data:
            content.append({'type': 'heading3', 'text': 'Key Deliverables'})
            for deliverable in plan_data['deliverables']:
                content.append({'type': 'numbered', 'text': deliverable})
            content.append({'type': 'paragraph', 'text': ''})
        
        # Add phases section
        if 'phases' in plan_data:
            content.append({'type': 'heading3', 'text': 'Project Phases'})
            for phase in plan_data['phases']:
                content.append({'type': 'heading3', 'text': phase['name']})
                content.append({'type': 'paragraph', 'text': f"Duration: {phase.get('duration', 'TBD')}"})
                if 'tasks' in phase:
                    for task in phase['tasks']:
                        content.append({'type': 'bullet', 'text': task})
                content.append({'type': 'paragraph', 'text': ''})
        
        return self.write_content(doc_id, content, append=False)
