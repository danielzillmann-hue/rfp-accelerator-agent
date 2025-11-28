"""
Gemini AI client for intelligent document analysis and content generation.
"""

from typing import Dict, List, Optional, Any

from google.cloud import aiplatform
from vertexai.generative_models import GenerativeModel, Part
import structlog


class GeminiClient:
    """
    Client for interacting with Gemini AI via Vertex AI.
    """
    
    def __init__(
        self,
        project_id: str,
        location: str = "us-central1",
        model_name: str = "gemini-1.5-pro-002",
        logger: Optional[structlog.BoundLogger] = None
    ):
        """
        Initialize Gemini AI client.
        
        Args:
            project_id: GCP project ID
            location: GCP region
            model_name: Gemini model name
            logger: Optional logger instance
        """
        self.logger = logger or structlog.get_logger(__name__)
        self.project_id = project_id
        self.location = location
        self.model_name = model_name
        
        # Initialize Vertex AI
        aiplatform.init(project=project_id, location=location)
        
        # Initialize the model
        self.model = GenerativeModel(model_name)
        
        self.logger.info(
            f"Gemini AI client initialized",
            project=project_id,
            model=model_name
        )
    
    def analyze_rfp_document(self, document_text: str) -> Dict[str, Any]:
        """
        Analyze an RFP document to extract key information.
        
        Args:
            document_text: Full text of the RFP document
        
        Returns:
            Dictionary with extracted information
        """
        prompt = f"""
        Analyze the following RFP document and extract key information.
        
        Please provide:
        1. Client/Organization name
        2. RFP title or project name
        3. RFP number (if available)
        4. Submission deadline
        5. Key requirements (top 5-7)
        6. Evaluation criteria
        7. Budget range (if mentioned)
        
        RFP Document:
        {document_text[:10000]}  # Limit to first 10k chars
        
        Respond in JSON format.
        """
        
        try:
            response = self.model.generate_content(prompt)
            result = self._parse_json_response(response.text)
            
            self.logger.info("Analyzed RFP document")
            return result
            
        except Exception as e:
            self.logger.error(f"Failed to analyze RFP: {e}")
            raise
    
    def generate_follow_up_questions(
        self,
        document_text: str,
        min_questions: int = 10,
        max_questions: int = 15
    ) -> List[Dict[str, str]]:
        """
        Generate follow-up questions based on RFP analysis.
        
        Args:
            document_text: Full text of the RFP document
            min_questions: Minimum number of questions
            max_questions: Maximum number of questions
        
        Returns:
            List of question dictionaries with category and question
        """
        prompt = f"""
        You are an expert RFP analyst. Review the following RFP document and identify {min_questions}-{max_questions} critical questions that need to be answered to create a comprehensive proposal.
        
        Focus on:
        - Ambiguous or vague requirements
        - Missing technical specifications
        - Unclear timelines or milestones
        - Integration requirements
        - Data formats and standards
        - Security and compliance details
        - Budget and pricing clarifications
        
        For each question, provide:
        - category: The category (e.g., "Technical Requirements", "Timeline", "Budget")
        - question: The specific question
        
        RFP Document:
        {document_text[:15000]}
        
        Respond with a JSON array of objects with "category" and "question" fields.
        """
        
        try:
            response = self.model.generate_content(prompt)
            questions = self._parse_json_response(response.text)
            
            self.logger.info(f"Generated {len(questions)} follow-up questions")
            return questions
            
        except Exception as e:
            self.logger.error(f"Failed to generate questions: {e}")
            raise
    
    def generate_draft_answers(
        self,
        rfp_questions: List[str],
        company_info: Dict[str, str],
        internal_knowledge: Optional[str] = None
    ) -> List[Dict[str, str]]:
        """
        Generate draft answers to RFP questions.
        
        Args:
            rfp_questions: List of questions from the RFP
            company_info: Company information dictionary
            internal_knowledge: Optional internal knowledge base text
        
        Returns:
            List of answer dictionaries with question and answer
        """
        company_context = f"""
        Company Information:
        - Name: {company_info.get('name', 'N/A')}
        - Address: {company_info.get('address', 'N/A')}
        - Website: {company_info.get('website', 'N/A')}
        """
        
        if internal_knowledge:
            company_context += f"\n\nInternal Knowledge:\n{internal_knowledge[:5000]}"
        
        answers = []
        
        for question in rfp_questions:
            prompt = f"""
            You are writing a professional RFP response. Generate a draft answer to the following question.
            
            {company_context}
            
            Question: {question}
            
            Provide a professional, detailed answer. Use [PLACEHOLDER: specific detail] for information that needs to be customized.
            
            Respond with just the answer text, no additional formatting.
            """
            
            try:
                response = self.model.generate_content(prompt)
                answer_text = response.text.strip()
                
                answers.append({
                    'question': question,
                    'answer': answer_text
                })
                
            except Exception as e:
                self.logger.error(f"Failed to generate answer for question: {e}")
                answers.append({
                    'question': question,
                    'answer': '[ERROR: Failed to generate answer]'
                })
        
        self.logger.info(f"Generated {len(answers)} draft answers")
        return answers
    
    def extract_project_timeline(self, document_text: str) -> Dict[str, Any]:
        """
        Extract timeline, milestones, and deliverables from RFP.
        
        Args:
            document_text: Full text of the RFP document
        
        Returns:
            Dictionary with timeline, milestones, and deliverables
        """
        prompt = f"""
        Analyze the following RFP document and extract all timeline-related information.
        
        Please identify:
        1. Key deadlines and dates
        2. Project milestones
        3. Required deliverables
        4. Project phases (if mentioned)
        
        RFP Document:
        {document_text[:15000]}
        
        Respond in JSON format with fields: timeline, milestones, deliverables, phases
        """
        
        try:
            response = self.model.generate_content(prompt)
            result = self._parse_json_response(response.text)
            
            self.logger.info("Extracted project timeline")
            return result
            
        except Exception as e:
            self.logger.error(f"Failed to extract timeline: {e}")
            raise
    
    def create_project_plan(
        self,
        timeline_data: Dict[str, Any],
        default_phases: List[str]
    ) -> Dict[str, Any]:
        """
        Create a preliminary project plan based on timeline data.
        
        Args:
            timeline_data: Extracted timeline information
            default_phases: Default project phases to use
        
        Returns:
            Structured project plan
        """
        prompt = f"""
        Create a preliminary project plan based on the following information.
        
        Timeline Data:
        {timeline_data}
        
        Default Phases:
        {default_phases}
        
        Create a structured project plan with:
        1. Phases with estimated durations
        2. Key tasks for each phase
        3. Resource allocation estimates
        4. Dependencies between phases
        
        Respond in JSON format.
        """
        
        try:
            response = self.model.generate_content(prompt)
            plan = self._parse_json_response(response.text)
            
            self.logger.info("Created project plan")
            return plan
            
        except Exception as e:
            self.logger.error(f"Failed to create project plan: {e}")
            raise
    
    def _parse_json_response(self, response_text: str) -> Any:
        """Parse JSON from model response, handling markdown code blocks."""
        import json
        import re
        
        # Remove markdown code blocks if present
        text = response_text.strip()
        
        # Try to extract JSON from markdown code block
        json_match = re.search(r'```(?:json)?\s*(\{.*\}|\[.*\])\s*```', text, re.DOTALL)
        if json_match:
            text = json_match.group(1)
        
        # Try to parse as JSON
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            # If that fails, try to find JSON object/array in the text
            json_match = re.search(r'(\{.*\}|\[.*\])', text, re.DOTALL)
            if json_match:
                return json.loads(json_match.group(1))
            raise ValueError(f"Could not parse JSON from response: {text[:200]}")
