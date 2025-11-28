"""
Google Drive API client for managing folders and files.
"""

from typing import Dict, List, Optional, Any
from pathlib import Path

from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from googleapiclient.errors import HttpError
import structlog


class GoogleDriveClient:
    """
    Client for interacting with Google Drive API.
    """
    
    def __init__(self, credentials_path: Optional[str] = None, logger: Optional[structlog.BoundLogger] = None):
        """
        Initialize Google Drive client.
        
        Args:
            credentials_path: Path to service account credentials JSON
            logger: Optional logger instance
        """
        self.logger = logger or structlog.get_logger(__name__)
        
        # Initialize credentials
        if credentials_path:
            credentials = service_account.Credentials.from_service_account_file(
                credentials_path,
                scopes=['https://www.googleapis.com/auth/drive']
            )
        else:
            # Use application default credentials
            from google.auth import default
            credentials, _ = default(scopes=['https://www.googleapis.com/auth/drive'])
        
        # Build the Drive service
        self.service = build('drive', 'v3', credentials=credentials)
        self.logger.info("Google Drive client initialized")
    
    def create_project_folder(
        self,
        folder_name: str,
        parent_folder_id: Optional[str] = None
    ) -> Dict[str, str]:
        """
        Create a project folder structure in Google Drive.
        
        Args:
            folder_name: Name of the main project folder
            parent_folder_id: Optional parent folder ID
        
        Returns:
            Dictionary with folder IDs and URLs
        """
        try:
            # Create main project folder
            main_folder = self._create_folder(folder_name, parent_folder_id)
            
            # Create subfolders
            subfolders = {
                'source_documents': self._create_folder(
                    '00_Source_Documents',
                    main_folder['id']
                ),
                'analysis': self._create_folder(
                    '01_Analysis',
                    main_folder['id']
                ),
                'planning': self._create_folder(
                    '02_Planning',
                    main_folder['id']
                ),
                'collaboration': self._create_folder(
                    '03_Collaboration',
                    main_folder['id']
                ),
            }
            
            self.logger.info(
                f"Created project folder structure: {folder_name}",
                folder_id=main_folder['id']
            )
            
            return {
                'main_folder_id': main_folder['id'],
                'main_folder_url': main_folder['url'],
                'subfolders': {
                    name: {'id': folder['id'], 'url': folder['url']}
                    for name, folder in subfolders.items()
                }
            }
            
        except HttpError as e:
            self.logger.error(f"Failed to create project folder: {e}")
            raise
    
    def _create_folder(self, name: str, parent_id: Optional[str] = None) -> Dict[str, str]:
        """Create a single folder."""
        file_metadata = {
            'name': name,
            'mimeType': 'application/vnd.google-apps.folder'
        }
        
        if parent_id:
            file_metadata['parents'] = [parent_id]
        
        folder = self.service.files().create(
            body=file_metadata,
            fields='id, webViewLink'
        ).execute()
        
        return {
            'id': folder['id'],
            'url': folder['webViewLink']
        }
    
    def upload_file(
        self,
        file_path: str,
        folder_id: str,
        file_name: Optional[str] = None
    ) -> Dict[str, str]:
        """
        Upload a file to Google Drive.
        
        Args:
            file_path: Local path to file
            folder_id: Destination folder ID
            file_name: Optional custom file name
        
        Returns:
            Dictionary with file ID and URL
        """
        try:
            path = Path(file_path)
            
            if not file_name:
                file_name = path.name
            
            file_metadata = {
                'name': file_name,
                'parents': [folder_id]
            }
            
            # Determine MIME type
            mime_types = {
                '.pdf': 'application/pdf',
                '.docx': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
                '.xlsx': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
                '.pptx': 'application/vnd.openxmlformats-officedocument.presentationml.presentation',
                '.txt': 'text/plain',
            }
            mime_type = mime_types.get(path.suffix.lower(), 'application/octet-stream')
            
            media = MediaFileUpload(file_path, mimetype=mime_type, resumable=True)
            
            file = self.service.files().create(
                body=file_metadata,
                media_body=media,
                fields='id, webViewLink'
            ).execute()
            
            self.logger.info(f"Uploaded file: {file_name}", file_id=file['id'])
            
            return {
                'id': file['id'],
                'url': file['webViewLink']
            }
            
        except HttpError as e:
            self.logger.error(f"Failed to upload file {file_path}: {e}")
            raise
    
    def share_folder(
        self,
        folder_id: str,
        email_addresses: List[str],
        role: str = 'writer'
    ) -> List[Dict[str, Any]]:
        """
        Share a folder with team members.
        
        Args:
            folder_id: Folder ID to share
            email_addresses: List of email addresses
            role: Permission role (reader, commenter, writer)
        
        Returns:
            List of permission results
        """
        results = []
        
        for email in email_addresses:
            try:
                permission = {
                    'type': 'user',
                    'role': role,
                    'emailAddress': email
                }
                
                result = self.service.permissions().create(
                    fileId=folder_id,
                    body=permission,
                    sendNotificationEmail=False,  # We'll send custom email
                    fields='id'
                ).execute()
                
                results.append({
                    'email': email,
                    'status': 'success',
                    'permission_id': result['id']
                })
                
                self.logger.info(f"Shared folder with {email}", folder_id=folder_id)
                
            except HttpError as e:
                self.logger.error(f"Failed to share with {email}: {e}")
                results.append({
                    'email': email,
                    'status': 'failed',
                    'error': str(e)
                })
        
        return results
    
    def get_file_metadata(self, file_id: str) -> Dict[str, Any]:
        """
        Get metadata for a file or folder.
        
        Args:
            file_id: File or folder ID
        
        Returns:
            File metadata dictionary
        """
        try:
            file = self.service.files().get(
                fileId=file_id,
                fields='id, name, mimeType, createdTime, modifiedTime, webViewLink, size'
            ).execute()
            
            return file
            
        except HttpError as e:
            self.logger.error(f"Failed to get file metadata: {e}")
            raise
