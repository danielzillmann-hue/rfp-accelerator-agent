"""
Base class for workflow steps.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any
import structlog


class WorkflowStep(ABC):
    """
    Abstract base class for workflow steps.
    """
    
    def __init__(self, config: Dict[str, Any], logger: structlog.BoundLogger):
        """
        Initialize workflow step.
        
        Args:
            config: Configuration dictionary
            logger: Logger instance
        """
        self.config = config
        self.logger = logger
    
    @abstractmethod
    def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute the workflow step.
        
        Args:
            context: Current workflow context
        
        Returns:
            Dictionary with step results and context updates
        """
        pass
    
    def _get_config_value(self, key_path: str, default: Any = None) -> Any:
        """
        Get a configuration value using dot notation.
        
        Args:
            key_path: Dot-separated path to config value (e.g., 'workflow.question_generation.min_questions')
            default: Default value if key not found
        
        Returns:
            Configuration value or default
        """
        keys = key_path.split('.')
        value = self.config
        
        for key in keys:
            if isinstance(value, dict) and key in value:
                value = value[key]
            else:
                return default
        
        return value
