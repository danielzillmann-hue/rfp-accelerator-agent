"""
Main RFP Accelerator Agent Orchestrator

This module contains the primary agent class that orchestrates the 7-step
workflow for transforming RFP documents into actionable project workspaces.
"""

import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any

import yaml

from .utils.logger import setup_logger
from .utils.validators import validate_email, validate_file_path
from .workflow import (
    IngestionStep,
    KnowledgeBaseStep,
    QuestionGenerationStep,
    AnswerGenerationStep,
    ProjectPlanStep,
    CollaborationStep,
    DistributionStep,
)


class RFPAcceleratorAgent:
    """
    RFP Accelerator Agent - Automated Project Kickoff Manager
    
    Transforms raw RFP documents into fully organized, team-ready,
    and actionable project workspaces through a 7-step orchestration workflow.
    """
    
    def __init__(
        self,
        gcp_project: str,
        config_path: Optional[str] = None,
        log_level: str = "INFO"
    ):
        """
        Initialize the RFP Accelerator Agent.
        
        Args:
            gcp_project: GCP project ID (e.g., 'gcp-sandpit-intelia')
            config_path: Path to configuration YAML file
            log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        """
        self.gcp_project = gcp_project
        self.logger = setup_logger(__name__, log_level)
        
        # Load configuration
        self.config = self._load_config(config_path)
        
        # Initialize workflow steps
        self._initialize_workflow_steps()
        
        # Workflow state
        self.state: Dict[str, Any] = {
            "status": "initialized",
            "current_step": 0,
            "results": {},
            "errors": [],
        }
        
        self.logger.info(
            f"RFP Accelerator Agent initialized for project: {gcp_project}"
        )
    
    def _load_config(self, config_path: Optional[str] = None) -> Dict[str, Any]:
        """Load configuration from YAML file."""
        if config_path is None:
            config_path = Path(__file__).parent.parent / "config.yaml"
        else:
            config_path = Path(config_path)
        
        if not config_path.exists():
            self.logger.warning(
                f"Config file not found at {config_path}, using defaults"
            )
            return self._get_default_config()
        
        with open(config_path, 'r') as f:
            config = yaml.safe_load(f)
        
        self.logger.info(f"Configuration loaded from {config_path}")
        return config
    
    def _get_default_config(self) -> Dict[str, Any]:
        """Return default configuration."""
        return {
            "gcp_project": self.gcp_project,
            "gemini_model": "gemini-1.5-pro-002",
            "workflow": {
                "question_generation": {
                    "min_questions": 10,
                    "max_questions": 15,
                }
            }
        }
    
    def _initialize_workflow_steps(self):
        """Initialize all workflow step handlers."""
        self.steps = {
            1: IngestionStep(self.config, self.logger),
            2: KnowledgeBaseStep(self.config, self.logger),
            3: QuestionGenerationStep(self.config, self.logger),
            4: AnswerGenerationStep(self.config, self.logger),
            5: ProjectPlanStep(self.config, self.logger),
            6: CollaborationStep(self.config, self.logger),
            7: DistributionStep(self.config, self.logger),
        }
        
        self.logger.debug("Workflow steps initialized")
    
    def execute_workflow(
        self,
        rfp_files: List[str],
        client_name: str,
        rfp_title: str,
        team_members: Optional[List[str]] = None,
        steps_to_run: Optional[List[int]] = None,
    ) -> Dict[str, Any]:
        """
        Execute the complete 7-step RFP acceleration workflow.
        
        Args:
            rfp_files: List of paths to RFP document files
            client_name: Name of the client organization
            rfp_title: Title of the RFP
            team_members: Optional list of team member email addresses
            steps_to_run: Optional list of specific steps to run (1-7)
        
        Returns:
            Dictionary containing workflow results and resource URLs
        """
        self.logger.info("=" * 80)
        self.logger.info("Starting RFP Accelerator Workflow")
        self.logger.info(f"Client: {client_name}")
        self.logger.info(f"RFP Title: {rfp_title}")
        self.logger.info(f"Files: {len(rfp_files)}")
        self.logger.info("=" * 80)
        
        # Validate inputs
        self._validate_inputs(rfp_files, client_name, rfp_title, team_members)
        
        # Determine which steps to run
        if steps_to_run is None:
            steps_to_run = list(range(1, 8))  # All steps 1-7
        
        # Initialize workflow context
        context = {
            "rfp_files": rfp_files,
            "client_name": client_name,
            "rfp_title": rfp_title,
            "date": datetime.now().strftime("%Y-%m-%d"),
            "team_members": team_members or [],
            "gcp_project": self.gcp_project,
        }
        
        try:
            # Execute each step sequentially
            for step_num in steps_to_run:
                self.state["current_step"] = step_num
                context = self._execute_step(step_num, context)
            
            self.state["status"] = "completed"
            self.logger.info("=" * 80)
            self.logger.info("RFP Accelerator Workflow Completed Successfully!")
            self.logger.info("=" * 80)
            
            return {
                "status": "success",
                "context": context,
                "results": self.state["results"],
            }
            
        except Exception as e:
            self.state["status"] = "failed"
            self.state["errors"].append(str(e))
            self.logger.error(f"Workflow failed at step {self.state['current_step']}: {e}")
            raise
    
    def _execute_step(self, step_num: int, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute a single workflow step.
        
        Args:
            step_num: Step number (1-7)
            context: Current workflow context
        
        Returns:
            Updated context with step results
        """
        step = self.steps[step_num]
        step_name = step.__class__.__name__
        
        self.logger.info(f"\n{'=' * 80}")
        self.logger.info(f"STEP {step_num}: {step_name}")
        self.logger.info(f"{'=' * 80}")
        
        try:
            # Execute the step
            result = step.execute(context)
            
            # Update context and state
            context.update(result.get("context_updates", {}))
            self.state["results"][f"step_{step_num}"] = result
            
            self.logger.info(f"✓ Step {step_num} completed successfully")
            
            return context
            
        except Exception as e:
            self.logger.error(f"✗ Step {step_num} failed: {e}")
            raise
    
    def _validate_inputs(
        self,
        rfp_files: List[str],
        client_name: str,
        rfp_title: str,
        team_members: Optional[List[str]],
    ):
        """Validate all input parameters."""
        # Validate files
        if not rfp_files:
            raise ValueError("At least one RFP file must be provided")
        
        for file_path in rfp_files:
            if not validate_file_path(file_path):
                raise ValueError(f"Invalid or non-existent file: {file_path}")
        
        # Validate client name and title
        if not client_name or not client_name.strip():
            raise ValueError("Client name cannot be empty")
        
        if not rfp_title or not rfp_title.strip():
            raise ValueError("RFP title cannot be empty")
        
        # Validate team members
        if team_members:
            for email in team_members:
                if not validate_email(email):
                    raise ValueError(f"Invalid email address: {email}")
        
        self.logger.debug("Input validation passed")
    
    def get_status(self) -> Dict[str, Any]:
        """
        Get current workflow status.
        
        Returns:
            Dictionary containing current status and progress
        """
        return {
            "status": self.state["status"],
            "current_step": self.state["current_step"],
            "total_steps": 7,
            "progress_percent": (self.state["current_step"] / 7) * 100,
            "errors": self.state["errors"],
        }
    
    def resume_workflow(self, context: Dict[str, Any], from_step: int = 1):
        """
        Resume a previously interrupted workflow.
        
        Args:
            context: Previous workflow context
            from_step: Step number to resume from (1-7)
        """
        self.logger.info(f"Resuming workflow from step {from_step}")
        
        steps_to_run = list(range(from_step, 8))
        
        return self.execute_workflow(
            rfp_files=context["rfp_files"],
            client_name=context["client_name"],
            rfp_title=context["rfp_title"],
            team_members=context.get("team_members"),
            steps_to_run=steps_to_run,
        )
