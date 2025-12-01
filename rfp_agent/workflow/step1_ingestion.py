"""
Step 1: Ingestion & Setup
Creates project folder structure and uploads RFP documents.
"""

from typing import Dict, Any
from datetime import datetime

from .base_step import WorkflowStep
from ..integrations.google_drive import GoogleDriveClient
from ..utils.document_parser import DocumentParser
from ..utils.validators import sanitize_folder_name


class IngestionStep(WorkflowStep):
    """Step 1: Ingestion & Setup"""
    
    def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute ingestion and setup step.
        
        Creates folder structure and uploads RFP documents.
        """
        self.logger.info("Executing Step 1: Ingestion & Setup")
        
        # Initialize Google Drive client
        drive_client = GoogleDriveClient(logger=self.logger)
        
        # Create folder name
        folder_name = self._create_folder_name(
            context['client_name'],
            context['rfp_title'],
            context['date']
        )
        
        # Create project folder structure
        parent_folder_id = self._get_config_value('drive_parent_folder_id')
        folder_structure = drive_client.create_project_folder(
            folder_name,
            parent_folder_id
        )
        
        self.logger.info(f"Created project folder: {folder_name}")
        
        # Parse and upload RFP documents
        uploaded_files = []
        source_folder_id = folder_structure['subfolders']['source_documents']['id']
        
        for file_path in context['rfp_files']:
            # Parse document to extract metadata and any derived files
            doc_info = DocumentParser.parse_document(file_path)
            
            # Upload original to Drive
            file_result = drive_client.upload_file(
                file_path,
                source_folder_id
            )
            
            uploaded_files.append({
                'name': doc_info['file_info']['name'],
                'id': file_result['id'],
                'url': file_result['url'],
                'metadata': doc_info.get('metadata', {})
            })
            
            self.logger.info(f"Uploaded: {doc_info['file_info']['name']}")

            # If the parser produced NotebookLM-friendly derivatives (e.g., from Excel), upload those too
            derived_files = doc_info.get('derived_files', {})
            for label, derived_path in derived_files.items():
                try:
                    derived_result = drive_client.upload_file(
                        derived_path,
                        source_folder_id
                    )
                    uploaded_files.append({
                        'name': Path(derived_path).name,
                        'id': derived_result['id'],
                        'url': derived_result['url'],
                        'metadata': {
                            'derived_from': doc_info['file_info']['name'],
                            'variant': label,
                        },
                    })
                    self.logger.info(f"Uploaded derived file for NotebookLM: {derived_path}")
                except Exception as e:
                    self.logger.warning(f"Failed to upload derived file {derived_path}: {e}")
        
        # Try to extract client info from first document
        if uploaded_files:
            first_doc = DocumentParser.parse_document(context['rfp_files'][0])
            extracted_info = DocumentParser.extract_client_info(first_doc['text'])
            
            # Update context with extracted info if not already set
            if extracted_info.get('client_name') and not context.get('client_name_confirmed'):
                context['extracted_client_name'] = extracted_info['client_name']
            if extracted_info.get('rfp_title') and not context.get('rfp_title_confirmed'):
                context['extracted_rfp_title'] = extracted_info['rfp_title']
        
        return {
            'status': 'success',
            'folder_structure': folder_structure,
            'uploaded_files': uploaded_files,
            'context_updates': {
                'folder_id': folder_structure['main_folder_id'],
                'folder_url': folder_structure['main_folder_url'],
                'folder_name': folder_name,
                'subfolders': folder_structure['subfolders'],
                'uploaded_files': uploaded_files,
            }
        }
    
    def _create_folder_name(self, client_name: str, rfp_title: str, date: str) -> str:
        """Create sanitized folder name."""
        template = self._get_config_value(
            'drive_folder_template',
            '{client_name} - {rfp_title} - {date}'
        )
        
        folder_name = template.format(
            client_name=client_name,
            rfp_title=rfp_title,
            date=date
        )
        
        return sanitize_folder_name(folder_name)
