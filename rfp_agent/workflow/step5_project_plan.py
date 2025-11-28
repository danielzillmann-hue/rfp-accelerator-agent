"""
Step 5: Initial Project Plan
Extracts timeline and creates preliminary project plan.
"""

from typing import Dict, Any

from .base_step import WorkflowStep
from ..integrations.gemini_ai import GeminiClient
from ..integrations.google_docs import GoogleDocsClient
from ..utils.document_parser import DocumentParser


class ProjectPlanStep(WorkflowStep):
    """Step 5: Initial Project Plan"""
    
    def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute project plan creation step.
        
        Extracts timeline from RFP and creates preliminary project plan.
        """
        self.logger.info("Executing Step 5: Initial Project Plan")
        
        # Initialize clients
        gemini_client = GeminiClient(
            project_id=context['gcp_project'],
            model_name=self._get_config_value('gemini_model', 'gemini-1.5-pro-002'),
            logger=self.logger
        )
        
        docs_client = GoogleDocsClient(logger=self.logger)
        
        # Parse all RFP documents and combine text
        combined_text = ""
        for file_path in context['rfp_files']:
            doc_info = DocumentParser.parse_document(file_path)
            combined_text += doc_info['text']
        
        # Extract timeline information
        self.logger.info("Extracting timeline and milestones from RFP")
        timeline_data = gemini_client.extract_project_timeline(combined_text)
        
        # Get default phases from config
        default_phases = self._get_config_value(
            'workflow.project_planning.default_phases',
            [
                "Discovery & Requirements",
                "Design & Architecture",
                "Development & Implementation",
                "Testing & QA",
                "Deployment & Training",
                "Support & Maintenance"
            ]
        )
        
        # Create project plan
        self.logger.info("Creating preliminary project plan")
        project_plan = gemini_client.create_project_plan(
            timeline_data=timeline_data,
            default_phases=default_phases
        )
        
        # Merge timeline data into project plan
        if 'timeline' not in project_plan:
            project_plan['timeline'] = timeline_data.get('timeline', [])
        if 'deliverables' not in project_plan:
            project_plan['deliverables'] = timeline_data.get('deliverables', [])
        
        # Create Google Doc for project plan
        planning_folder_id = context['subfolders']['planning']['id']
        
        plan_doc = docs_client.create_document(
            title="Draft_Project_Plan",
            folder_id=planning_folder_id
        )
        
        # Write project plan to document
        docs_client.create_project_plan_document(
            doc_id=plan_doc['id'],
            plan_data=project_plan,
            client_name=context['client_name'],
            rfp_title=context['rfp_title']
        )
        
        self.logger.info(f"Created project plan document: {plan_doc['url']}")
        
        return {
            'status': 'success',
            'timeline_data': timeline_data,
            'project_plan': project_plan,
            'plan_doc': plan_doc,
            'context_updates': {
                'timeline_data': timeline_data,
                'project_plan': project_plan,
                'plan_doc_id': plan_doc['id'],
                'plan_doc_url': plan_doc['url'],
            }
        }
