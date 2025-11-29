
"""
Gemini AI client for intelligent document analysis and content generation.
Updated with Vertex AI Search Grounding support.
"""

from typing import Dict, List, Optional, Any
import json
import re
import structlog

from google.cloud import aiplatform
import vertexai
from vertexai.generative_models import GenerativeModel, Part, Tool, grounding


class GeminiClient:
    """
    Client for interacting with Gemini AI via Vertex AI.
    """
    
    def __init__(
        self,
        project_id: str,
        location: str = "us-central1",
        model_name: str = "gemini-1.5-pro-002",
        temperature: float = 0.7,
        max_tokens: int = 8192,
        logger: Optional[structlog.BoundLogger] = None
    ):
        """
        Initialize Gemini AI client.
        
        Args:
            project_id: GCP project ID
            location: GCP region
            model_name: Gemini model name
            temperature: Generation temperature
            max_tokens: Max output tokens
            logger: Optional logger instance
        """
        self.logger = logger or structlog.get_logger(__name__)
        self.project_id = project_id
        self.location = location
        self.model_name = model_name
        self.temperature = temperature
        self.max_tokens = max_tokens
        
        # Initialize Vertex AI
        vertexai.init(project=project_id, location=location)
        self.model = GenerativeModel(model_name)
        
        self.logger.info(f"Gemini AI client initialized with model: {model_name}")
    
    def generate_content(
        self, 
        prompt: str, 
        grounding_source: Optional[str] = None
    ) -> str:
        """
        Generate content using Gemini, optionally grounded by a Data Store.
        
        Args:
            prompt: The prompt to send to the model
            grounding_source: Optional Data Store resource name for RAG
            
        Returns:
            Generated text response
        """
        try:
            tools = None
            if grounding_source:
                # Configure retrieval tool for grounding
                tool = Tool.from_retrieval(
                    grounding.Retrieval(
                        source=grounding.VertexAISearch(datastore=grounding_source)
                    )
                )
                tools = [tool]
                self.logger.info(f"Using grounding source: {grounding_source}")

            response = self.model.generate_content(
                prompt,
                tools=tools,
                generation_config={
                    "temperature": self.temperature,
                    "max_output_tokens": self.max_tokens,
                }
            )
            
            return response.text
            
        except Exception as e:
            self.logger.error(f"Gemini generation failed: {e}")
            raise

    def analyze_rfp_document(self, document_text: str) -> Dict[str, Any]:
        """
        Analyze RFP document text to extract key information.
        """
        prompt = f"""
        Analyze the following Request for Proposal (RFP) document and extract the following information in JSON format:
        - client_name: The name of the organization issuing the RFP
        - rfp_title: The title of the RFP
        - submission_deadline: The due date for the proposal (YYYY-MM-DD format if possible)
        - key_objectives: A list of 3-5 primary goals of the project
        - required_technologies: A list of specific technologies mentioned (if any)
        
        Document Text:
        {document_text[:30000]}
        """
        
        response_text = self.generate_content(prompt)
        return self._parse_json_response(response_text)

    def generate_follow_up_questions(
        self,
        document_text: str,
        min_questions: int = 10,
        max_questions: int = 15,
        grounding_source: Optional[str] = None
    ) -> List[Dict[str, str]]:
        """
        Generate critical follow-up questions based on the RFP.
        Supports grounding via Vertex AI Search.
        """
        prompt = f"""
        You are an expert Proposal Manager. Analyze the RFP text below and identify {min_questions}-{max_questions} 
        critical ambiguities, missing data points, or vague requirements that need clarification.
        
        Focus on:
        1. Technical constraints
        2. Integration requirements
        3. Budget and timeline specifics
        4. Stakeholder roles
        
        Output a JSON list of objects, where each object has:
        - "category": The topic (e.g., "Technical", "Timeline", "Budget")
        - "question": The specific question to ask the client
        - "rationale": Why this question is critical (quote the relevant RFP section if possible)
        
        RFP Text Context:
        {document_text[:50000]}
        """
        
        # Use grounding if provided
        response_text = self.generate_content(prompt, grounding_source=grounding_source)
        return self._parse_json_response(response_text)

    def draft_rfp_answers(
        self,
        questions: List[str],
        company_info: Dict[str, str],
        internal_knowledge: str = "",
        grounding_source: Optional[str] = None
    ) -> List[Dict[str, str]]:
        """
        Draft answers for explicit RFP questions.
        Supports grounding via Vertex AI Search.
        """
        prompt = f"""
        Draft professional, persuasive answers for the following RFP questions.
        Use the provided Company Information and Internal Knowledge.
        
        Company Information:
        {json.dumps(company_info, indent=2)}
        
        Internal Knowledge Context:
        {internal_knowledge[:10000]}
        
        Questions to Answer:
        {json.dumps(questions, indent=2)}
        
        Output a JSON list of objects with:
        - "question": The original question
        - "draft_answer": The proposed response (use placeholders like [INSERT DATA] for missing info)
        - "confidence": High/Medium/Low based on available info
        """
        
        response_text = self.generate_content(prompt, grounding_source=grounding_source)
        return self._parse_json_response(response_text)

    def extract_timeline_and_plan(self, document_text: str) -> Dict[str, Any]:
        """
        Extract timeline and generate a preliminary project plan.
        """
        prompt = f"""
        Based on the RFP text, extract all deadlines and milestones. 
        Then, create a preliminary Work Breakdown Structure (WBS) and resource estimate.
        
        RFP Text:
        {document_text[:50000]}
        
        Output JSON with:
        - "key_dates": List of {{"event": "...", "date": "..."}}
        - "wbs": List of phases, each with a list of tasks
        - "resource_roles": List of required roles (e.g., "Project Manager", "Senior Dev")
        - "estimated_duration_weeks": Integer estimate
        """
        
        response_text = self.generate_content(prompt)
        return self._parse_json_response(response_text)

    def _parse_json_response(self, response_text: str) -> Any:
        """Helper to clean and parse JSON from LLM response."""
        try:
            # Remove markdown code blocks if present
            cleaned_text = re.sub(r'```json\s*|\s*```', '', response_text)
            return json.loads(cleaned_text)
        except json.JSONDecodeError as e:
            self.logger.error(f"Failed to parse JSON response: {e}")
            self.logger.debug(f"Raw response: {response_text}")
            return {}
