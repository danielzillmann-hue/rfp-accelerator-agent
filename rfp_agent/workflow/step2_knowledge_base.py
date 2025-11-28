"""
Step 2: Knowledge Base Creation
Creates NotebookLM notebook and adds RFP sources.
"""

from typing import Dict, Any

from .base_step import WorkflowStep
from ..integrations.notebooklm import NotebookLMClient


class KnowledgeBaseStep(WorkflowStep):
    """Step 2: Knowledge Base Creation"""
    
    def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute knowledge base creation step.
        
        Creates NotebookLM notebook and adds RFP documents as sources.
        """
        self.logger.info("Executing Step 2: Knowledge Base Creation")
        
        # Initialize NotebookLM client
        notebooklm_client = NotebookLMClient(
            project_id=context['gcp_project'],
            logger=self.logger
        )
        
        # Create notebook
        notebook_name = f"{context['client_name']} - {context['rfp_title']}"
        notebook = notebooklm_client.create_notebook(
            name=notebook_name,
            description=f"RFP Knowledge Base for {context['client_name']}"
        )
        
        self.logger.info(f"Created NotebookLM notebook: {notebook_name}")
        
        # Add source documents
        sources_added = []
        for file_info in context.get('uploaded_files', []):
            source_result = notebooklm_client.add_source(
                notebook_id=notebook['id'],
                source_url=file_info['url'],
                source_type='document'
            )
            sources_added.append(source_result)
            self.logger.info(f"Added source: {file_info['name']}")
        
        # Get notebook status
        status = notebooklm_client.get_notebook_status(notebook['id'])
        
        # Generate manual instructions if API is placeholder
        manual_instructions = None
        if notebook.get('status') == 'placeholder':
            file_names = [f['name'] for f in context.get('uploaded_files', [])]
            manual_instructions = NotebookLMClient.get_manual_instructions(
                notebook_name,
                file_names
            )
            self.logger.warning("NotebookLM API not available - manual setup required")
            self.logger.info(manual_instructions)
        
        return {
            'status': 'success',
            'notebook': notebook,
            'sources_added': sources_added,
            'notebook_status': status,
            'manual_instructions': manual_instructions,
            'context_updates': {
                'notebook_id': notebook['id'],
                'notebook_url': notebook['url'],
                'notebooklm_manual_setup': manual_instructions,
            }
        }
