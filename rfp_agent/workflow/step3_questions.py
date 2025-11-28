"""
Step 3: Question Generation
Analyzes RFP and generates critical follow-up questions.
"""

from typing import Dict, Any

from .base_step import WorkflowStep
from ..integrations.gemini_ai import GeminiClient
from ..integrations.google_docs import GoogleDocsClient
from ..utils.document_parser import DocumentParser


class QuestionGenerationStep(WorkflowStep):
    """Step 3: Question Generation"""
    
    def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute question generation step.
        
        Analyzes RFP documents and generates critical follow-up questions.
        """
        self.logger.info("Executing Step 3: Question Generation")
        
        # Initialize clients
        gemini_client = GeminiClient(
            project_id=context['gcp_project'],
            model_name=self._get_config_value('gemini_model', 'gemini-1.5-pro-002'),
            logger=self.logger
        )
        
        docs_client = GoogleDocsClient(logger=self.logger)
        
        # Parse all RFP documents and combine text
        combined_text = ""
        for file_path in context['rfp_files']:
            doc_info = DocumentParser.parse_document(file_path)
            combined_text += f"\n\n=== {doc_info['file_info']['name']} ===\n\n"
            combined_text += doc_info['text']
        
        self.logger.info(f"Analyzing {len(context['rfp_files'])} RFP documents")
        
        # Generate questions using Gemini
        min_questions = self._get_config_value('workflow.question_generation.min_questions', 10)
        max_questions = self._get_config_value('workflow.question_generation.max_questions', 15)
        
        questions = gemini_client.generate_follow_up_questions(
            document_text=combined_text,
            min_questions=min_questions,
            max_questions=max_questions
        )
        
        self.logger.info(f"Generated {len(questions)} follow-up questions")
        
        # Create Google Doc for questions
        analysis_folder_id = context['subfolders']['analysis']['id']
        
        questions_doc = docs_client.create_document(
            title="Client_Follow-up_Questions",
            folder_id=analysis_folder_id
        )
        
        # Write questions to document
        docs_client.create_questions_document(
            doc_id=questions_doc['id'],
            questions=questions,
            client_name=context['client_name'],
            rfp_title=context['rfp_title']
        )
        
        self.logger.info(f"Created questions document: {questions_doc['url']}")
        
        return {
            'status': 'success',
            'questions': questions,
            'questions_doc': questions_doc,
            'context_updates': {
                'questions': questions,
                'questions_doc_id': questions_doc['id'],
                'questions_doc_url': questions_doc['url'],
            }
        }
