"""
Google Workspace API client for email notifications.
"""

import base64
from email.mime.text import MIMEText
from typing import Dict, List, Optional

from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import structlog


class GoogleWorkspaceClient:
    """
    Client for interacting with Google Workspace APIs (Gmail).
    """
    
    def __init__(
        self,
        credentials_path: Optional[str] = None,
        sender_email: Optional[str] = None,
        logger: Optional[structlog.BoundLogger] = None
    ):
        """
        Initialize Google Workspace client.
        
        Args:
            credentials_path: Path to service account credentials JSON
            sender_email: Email address to send from
            logger: Optional logger instance
        """
        self.logger = logger or structlog.get_logger(__name__)
        self.sender_email = sender_email
        
        # Initialize credentials
        if credentials_path:
            credentials = service_account.Credentials.from_service_account_file(
                credentials_path,
                scopes=['https://www.googleapis.com/auth/gmail.send']
            )
        else:
            from google.auth import default
            credentials, _ = default(scopes=['https://www.googleapis.com/auth/gmail.send'])
        
        # Build the Gmail service
        self.service = build('gmail', 'v1', credentials=credentials)
        self.logger.info("Google Workspace client initialized")
    
    def send_email(
        self,
        to_addresses: List[str],
        subject: str,
        body: str,
        html: bool = False,
        cc_addresses: Optional[List[str]] = None
    ) -> List[Dict[str, str]]:
        """
        Send email to multiple recipients.
        
        Args:
            to_addresses: List of recipient email addresses
            subject: Email subject
            body: Email body (plain text or HTML)
            html: Whether body is HTML
            cc_addresses: Optional CC recipients
        
        Returns:
            List of send results for each recipient
        """
        results = []
        
        for to_address in to_addresses:
            try:
                message = self._create_message(
                    to_address,
                    subject,
                    body,
                    html,
                    cc_addresses
                )
                
                sent_message = self.service.users().messages().send(
                    userId='me',
                    body=message
                ).execute()
                
                results.append({
                    'email': to_address,
                    'status': 'success',
                    'message_id': sent_message['id']
                })
                
                self.logger.info(f"Sent email to {to_address}", message_id=sent_message['id'])
                
            except HttpError as e:
                self.logger.error(f"Failed to send email to {to_address}: {e}")
                results.append({
                    'email': to_address,
                    'status': 'failed',
                    'error': str(e)
                })
        
        return results
    
    def _create_message(
        self,
        to: str,
        subject: str,
        body: str,
        html: bool = False,
        cc: Optional[List[str]] = None
    ) -> Dict:
        """Create a message for sending."""
        if html:
            message = MIMEText(body, 'html')
        else:
            message = MIMEText(body, 'plain')
        
        message['to'] = to
        message['subject'] = subject
        
        if self.sender_email:
            message['from'] = self.sender_email
        
        if cc:
            message['cc'] = ', '.join(cc)
        
        raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode('utf-8')
        
        return {'raw': raw_message}
    
    def send_project_notification(
        self,
        team_members: List[str],
        client_name: str,
        rfp_title: str,
        resources: Dict[str, str]
    ) -> List[Dict[str, str]]:
        """
        Send project kickoff notification to team members.
        
        Args:
            team_members: List of team member email addresses
            client_name: Client name
            rfp_title: RFP title
            resources: Dictionary of resource URLs
        
        Returns:
            List of send results
        """
        subject = f"New RFP Project: {client_name} - {rfp_title}"
        
        body = self._create_notification_body(
            client_name,
            rfp_title,
            resources
        )
        
        return self.send_email(
            to_addresses=team_members,
            subject=subject,
            body=body,
            html=True
        )
    
    def _create_notification_body(
        self,
        client_name: str,
        rfp_title: str,
        resources: Dict[str, str]
    ) -> str:
        """Create HTML email body for project notification."""
        html = f"""
        <html>
        <head>
            <style>
                body {{
                    font-family: Arial, sans-serif;
                    line-height: 1.6;
                    color: #333;
                }}
                .header {{
                    background-color: #4285f4;
                    color: white;
                    padding: 20px;
                    text-align: center;
                }}
                .content {{
                    padding: 20px;
                }}
                .resources {{
                    background-color: #f5f5f5;
                    padding: 15px;
                    margin: 20px 0;
                    border-left: 4px solid #4285f4;
                }}
                .resource-link {{
                    display: block;
                    margin: 10px 0;
                    color: #4285f4;
                    text-decoration: none;
                }}
                .resource-link:hover {{
                    text-decoration: underline;
                }}
                .footer {{
                    margin-top: 30px;
                    padding-top: 20px;
                    border-top: 1px solid #ddd;
                    font-size: 0.9em;
                    color: #666;
                }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1>🚀 New RFP Project Initiated</h1>
            </div>
            
            <div class="content">
                <h2>Project Details</h2>
                <p><strong>Client:</strong> {client_name}</p>
                <p><strong>RFP Title:</strong> {rfp_title}</p>
                
                <h2>What's Been Done</h2>
                <p>The RFP Accelerator Agent has automatically:</p>
                <ul>
                    <li>✓ Created a structured project workspace</li>
                    <li>✓ Organized all RFP source documents</li>
                    <li>✓ Generated a NotebookLM knowledge base</li>
                    <li>✓ Identified critical follow-up questions</li>
                    <li>✓ Drafted initial RFP responses</li>
                    <li>✓ Created a preliminary project plan</li>
                </ul>
                
                <div class="resources">
                    <h3>📁 Project Resources</h3>
        """
        
        # Add resource links
        if 'folder_url' in resources:
            html += f'<a href="{resources["folder_url"]}" class="resource-link">📂 Project Folder</a>'
        
        if 'notebook_url' in resources:
            html += f'<a href="{resources["notebook_url"]}" class="resource-link">📚 NotebookLM Knowledge Base</a>'
        
        if 'questions_doc_url' in resources:
            html += f'<a href="{resources["questions_doc_url"]}" class="resource-link">❓ Follow-up Questions</a>'
        
        if 'answers_doc_url' in resources:
            html += f'<a href="{resources["answers_doc_url"]}" class="resource-link">📝 Draft Responses</a>'
        
        if 'plan_doc_url' in resources:
            html += f'<a href="{resources["plan_doc_url"]}" class="resource-link">📅 Project Plan</a>'
        
        html += """
                </div>
                
                <h2>Next Steps</h2>
                <ol>
                    <li>Review the generated follow-up questions</li>
                    <li>Customize the draft responses</li>
                    <li>Refine the project plan timeline</li>
                    <li>Explore the NotebookLM knowledge base</li>
                    <li>Schedule a kickoff meeting</li>
                </ol>
                
                <div class="footer">
                    <p>This is an automated notification from the RFP Accelerator Agent.</p>
                    <p>If you have any questions, please contact your project manager.</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        return html
