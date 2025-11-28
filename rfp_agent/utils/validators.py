"""
Input validation utilities for the RFP Accelerator Agent.
"""

import re
from pathlib import Path
from typing import List


def validate_email(email: str) -> bool:
    """
    Validate an email address format.
    
    Args:
        email: Email address to validate
    
    Returns:
        True if valid, False otherwise
    """
    if not email or not isinstance(email, str):
        return False
    
    # RFC 5322 compliant email regex (simplified)
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email.strip()))


def validate_file_path(file_path: str) -> bool:
    """
    Validate that a file path exists and is readable.
    
    Args:
        file_path: Path to file
    
    Returns:
        True if valid and exists, False otherwise
    """
    if not file_path or not isinstance(file_path, str):
        return False
    
    path = Path(file_path)
    return path.exists() and path.is_file()


def validate_file_extension(file_path: str, allowed_extensions: List[str]) -> bool:
    """
    Validate that a file has an allowed extension.
    
    Args:
        file_path: Path to file
        allowed_extensions: List of allowed extensions (e.g., ['.pdf', '.docx'])
    
    Returns:
        True if extension is allowed, False otherwise
    """
    if not file_path:
        return False
    
    path = Path(file_path)
    return path.suffix.lower() in [ext.lower() for ext in allowed_extensions]


def validate_file_size(file_path: str, max_size_mb: int = 50) -> bool:
    """
    Validate that a file is not too large.
    
    Args:
        file_path: Path to file
        max_size_mb: Maximum file size in megabytes
    
    Returns:
        True if file size is acceptable, False otherwise
    """
    if not validate_file_path(file_path):
        return False
    
    path = Path(file_path)
    size_mb = path.stat().st_size / (1024 * 1024)
    return size_mb <= max_size_mb


def sanitize_folder_name(name: str) -> str:
    """
    Sanitize a string to be used as a folder name.
    
    Args:
        name: Raw folder name
    
    Returns:
        Sanitized folder name safe for file systems
    """
    # Remove or replace invalid characters
    invalid_chars = r'[<>:"/\\|?*]'
    sanitized = re.sub(invalid_chars, '_', name)
    
    # Remove leading/trailing spaces and dots
    sanitized = sanitized.strip('. ')
    
    # Limit length
    max_length = 200
    if len(sanitized) > max_length:
        sanitized = sanitized[:max_length]
    
    return sanitized


def validate_gcp_project_id(project_id: str) -> bool:
    """
    Validate a GCP project ID format.
    
    Args:
        project_id: GCP project ID
    
    Returns:
        True if valid format, False otherwise
    """
    if not project_id or not isinstance(project_id, str):
        return False
    
    # GCP project ID rules:
    # - 6-30 characters
    # - Lowercase letters, digits, hyphens
    # - Must start with a letter
    # - Cannot end with a hyphen
    pattern = r'^[a-z][a-z0-9-]{4,28}[a-z0-9]$'
    return bool(re.match(pattern, project_id))
