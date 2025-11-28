"""
Step 6: Collaboration Prompt
Prompts for and validates team member information.
"""

from typing import Dict, Any, List

from .base_step import WorkflowStep
from ..utils.validators import validate_email


class CollaborationStep(WorkflowStep):
    """Step 6: Collaboration Prompt"""
    
    def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute collaboration prompt step.
        
        Prompts for team member emails if not already provided.
        """
        self.logger.info("Executing Step 6: Collaboration Prompt")
        
        # Check if team members already provided
        team_members = context.get('team_members', [])
        
        if not team_members:
            self.logger.info("No team members provided in context")
            
            # In a real implementation, this would prompt the user
            # For now, we'll just log that manual input is required
            self.logger.warning(
                "Team member emails required. Please provide via context or interactive prompt."
            )
            
            # Return with instruction for manual input
            return {
                'status': 'pending_input',
                'message': 'Team member email addresses required',
                'prompt': 'Please provide a list of team member email addresses to share the project with.',
                'context_updates': {
                    'awaiting_team_members': True,
                }
            }
        
        # Validate all email addresses
        validated_members = []
        invalid_emails = []
        
        for email in team_members:
            if validate_email(email):
                validated_members.append(email)
                self.logger.info(f"Validated team member: {email}")
            else:
                invalid_emails.append(email)
                self.logger.warning(f"Invalid email address: {email}")
        
        if invalid_emails:
            self.logger.error(f"Found {len(invalid_emails)} invalid email addresses")
            return {
                'status': 'validation_failed',
                'validated_members': validated_members,
                'invalid_emails': invalid_emails,
                'message': f'Invalid email addresses: {", ".join(invalid_emails)}',
                'context_updates': {
                    'validated_team_members': validated_members,
                    'invalid_team_members': invalid_emails,
                }
            }
        
        self.logger.info(f"Validated {len(validated_members)} team members")
        
        return {
            'status': 'success',
            'validated_members': validated_members,
            'context_updates': {
                'validated_team_members': validated_members,
                'awaiting_team_members': False,
            }
        }
