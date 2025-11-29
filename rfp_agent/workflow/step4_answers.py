
"""
Step 4: Draft Answer Generation
Generates draft answers to RFP questions using internal knowledge.
"""

from typing import Dict, Any, List
import re

from .base_step import WorkflowStep
from ..integrations.gemini_ai import GeminiClient
from ..integrations.google_docs import GoogleDocsClient
from ..utils.document_parser import DocumentParser


class AnswerGenerationStep(WorkflowStep):
    """Step 4: Draft Answer Generation"""
    
    def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute draft answer generation step.
        
        Extracts RFP questions and generates draft answers.
        """
        self.logger.info("Executing Step 4: Draft Answer Generation")
        
        # Initialize clients
        gemini_client = GeminiClient(
            project_id=context['gcp_project'],
            model_name=self._get_config_value('gemini_model', 'gemini-1.5-pro-002'),
            logger=self.logger
        )
        
        docs_client = GoogleDocsClient(logger=self.logger)
        
        # Parse RFP documents to extract questions
        combined_text = ""
        for file_path in context['rfp_files']:
            doc_info = DocumentParser.parse_document(file_path)
            combined_text += doc_info['text']
        
        # Extract questions from RFP
        rfp_questions = self._extract_questions_from_rfp(combined_text)
        
        self.logger.info(f"Extracted {len(rfp_questions)} questions from RFP")
        
        # Get company info from config
        company_info = self._get_config_value('company_info', {})
        
        # Load internal knowledge if available
        internal_knowledge = self._load_internal_knowledge()
        
        # Get grounding source if available
        grounding_source = context.get('grounding_source')
        if grounding_source:
            self.logger.info(f"Using grounding source: {grounding_source}")
        
        # Generate draft answers
        draft_answers = gemini_client.draft_rfp_answers(
            questions=rfp_questions,
            company_info=company_info,
            internal_knowledge=internal_knowledge,
            grounding_source=grounding_source
        )
        
        self.logger.info(f"Generated {len(draft_answers)} draft answers")
        
        # Create Google Doc for answers
        analysis_folder_id = context['subfolders']['analysis']['id']
        
        answers_doc = docs_client.create_document(
            title="Draft_RFP_Answers",
            folder_id=analysis_folder_id
        )
        
        # Write answers to document
        docs_client.create_answers_document(
            doc_id=answers_doc['id'],
            answers=draft_answers,
            client_name=context['client_name'],
            rfp_title=context['rfp_title']
        )
        
        self.logger.info(f"Created answers document: {answers_doc['url']}")
        
        return {
            'status': 'success',
            'draft_answers': draft_answers,
            'answers_doc': answers_doc,
            'context_updates': {
                'draft_answers': draft_answers,
                'answers_doc_id': answers_doc['id'],
                'answers_doc_url': answers_doc['url'],
            }
        }
    
    def _extract_questions_from_rfp(self, text: str) -> List[str]:
        """
        Extract questions from RFP text using pattern matching.
        """
        questions = []
        lines = text.split('\n')
        
        # Pattern 1: Lines ending with question marks
        for line in lines:
            line = line.strip()
            if line.endswith('?') and len(line) > 20:
                clean_line = re.sub(r'^\d+[\.\)]\s*', '', line)
                questions.append(clean_line)
        
        # Pattern 2: Lines starting with common question words
        question_starters = ['describe', 'explain', 'provide', 'list', 'detail', 'outline']
        for line in lines:
            line = line.strip()
            if any(line.lower().startswith(word) for word in question_starters):
                if len(line) > 30 and len(line) < 300:
                    clean_line = re.sub(r'^\d+[\.\)]\s*', '', line)
                    if clean_line not in questions:
                        questions.append(clean_line)
        
        if len(questions) > 20:
            questions = questions[:20]
        
        if not questions:
            questions = [
                "Describe your company's experience with similar projects.",
                "Provide details about your proposed methodology and approach.",
                "List the key team members and their qualifications.",
                "Explain your project timeline and milestones.",
                "Describe your quality assurance processes.",
            ]
        
        return questions
    
    def _load_internal_knowledge(self) -> str:
        """Load internal knowledge base content."""
        knowledge_config = self._get_config_value('internal_knowledge_source', {})
        if not knowledge_config:
            return ""
        self.logger.info("Internal knowledge source not configured")
        return ""
