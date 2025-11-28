"""
Step 7: Distribution & Launch
Shares resources with team and sends notification emails.
"""

from typing import Dict, Any

from .base_step import WorkflowStep
from ..integrations.google_drive import GoogleDriveClient
from ..integrations.notebooklm import NotebookLMClient
from ..integrations.google_workspace import GoogleWorkspaceClient


class DistributionStep(WorkflowStep):
    """Step 7: Distribution & Launch"""
    
    def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute distribution and launch step.
        
        Shares all resources with team members and sends notifications.
        """
        self.logger.info("Executing Step 7: Distribution & Launch")
        
        # Get validated team members
        team_members = context.get('validated_team_members', [])
        
        if not team_members:
            self.logger.warning("No team members to share with")
            return {
                'status': 'skipped',
                'message': 'No team members provided - skipping distribution',
                'context_updates': {}
            }
        
        # Initialize clients
        drive_client = GoogleDriveClient(logger=self.logger)
        notebooklm_client = NotebookLMClient(
            project_id=context['gcp_project'],
            logger=self.logger
        )
        workspace_client = GoogleWorkspaceClient(
            sender_email=self._get_config_value('email_sender'),
            logger=self.logger
        )
        
        # Share project folder
        share_permission = self._get_config_value('workflow.distribution.share_permissions', 'writer')
        
        self.logger.info(f"Sharing project folder with {len(team_members)} team members")
        folder_share_results = drive_client.share_folder(
            folder_id=context['folder_id'],
            email_addresses=team_members,
            role=share_permission
        )
        
        # Share NotebookLM notebook
        self.logger.info("Sharing NotebookLM notebook")
        notebook_share_results = notebooklm_client.share_notebook(
            notebook_id=context['notebook_id'],
            email_addresses=team_members,
            role='viewer'
        )
        
        # Prepare resource URLs for email
        resources = {
            'folder_url': context.get('folder_url'),
            'notebook_url': context.get('notebook_url'),
            'questions_doc_url': context.get('questions_doc_url'),
            'answers_doc_url': context.get('answers_doc_url'),
            'plan_doc_url': context.get('plan_doc_url'),
        }
        
        # Send notification emails
        email_enabled = self._get_config_value('email_enabled', True)
        email_results = []
        
        if email_enabled:
            self.logger.info("Sending notification emails")
            email_results = workspace_client.send_project_notification(
                team_members=team_members,
                client_name=context['client_name'],
                rfp_title=context['rfp_title'],
                resources=resources
            )
        else:
            self.logger.info("Email notifications disabled in config")
        
        # Compile results
        successful_shares = sum(1 for r in folder_share_results if r['status'] == 'success')
        successful_emails = sum(1 for r in email_results if r['status'] == 'success')
        
        self.logger.info(
            f"Distribution complete: {successful_shares}/{len(team_members)} shares, "
            f"{successful_emails}/{len(team_members)} emails sent"
        )
        
        return {
            'status': 'success',
            'folder_share_results': folder_share_results,
            'notebook_share_results': notebook_share_results,
            'email_results': email_results,
            'summary': {
                'team_members_count': len(team_members),
                'successful_shares': successful_shares,
                'successful_emails': successful_emails,
            },
            'context_updates': {
                'distribution_complete': True,
                'folder_share_results': folder_share_results,
                'email_results': email_results,
            }
        }
