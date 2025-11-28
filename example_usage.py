"""
Example usage of the RFP Accelerator Agent.
"""

from rfp_agent import RFPAcceleratorAgent

# Example 1: Basic usage with all steps
def example_basic():
    """Basic usage example."""
    
    agent = RFPAcceleratorAgent(
        gcp_project="gcp-sandpit-intelia",
        config_path="config.yaml"
    )
    
    result = agent.execute_workflow(
        rfp_files=[
            "path/to/rfp_document.pdf",
            "path/to/rfp_appendix.docx"
        ],
        client_name="Acme Corporation",
        rfp_title="Digital Transformation Initiative",
        team_members=[
            "project.manager@company.com",
            "lead.analyst@company.com",
            "tech.lead@company.com"
        ]
    )
    
    print(f"Project Folder: {result['context']['folder_url']}")
    print(f"NotebookLM: {result['context']['notebook_url']}")
    print(f"Questions: {result['context']['questions_doc_url']}")


# Example 2: Running specific steps only
def example_specific_steps():
    """Run only specific workflow steps."""
    
    agent = RFPAcceleratorAgent(
        gcp_project="gcp-sandpit-intelia"
    )
    
    # Run only steps 1-3 (setup, knowledge base, questions)
    result = agent.execute_workflow(
        rfp_files=["path/to/rfp.pdf"],
        client_name="Beta Industries",
        rfp_title="Cloud Migration Project",
        steps_to_run=[1, 2, 3]
    )
    
    print(f"Completed steps 1-3")
    print(f"Questions generated: {len(result['context']['questions'])}")


# Example 3: Resume workflow from a specific step
def example_resume():
    """Resume a previously interrupted workflow."""
    
    agent = RFPAcceleratorAgent(
        gcp_project="gcp-sandpit-intelia"
    )
    
    # Load previous context (in practice, this would be saved)
    previous_context = {
        'rfp_files': ["path/to/rfp.pdf"],
        'client_name': "Gamma Corp",
        'rfp_title': "AI Implementation",
        'folder_id': "previous-folder-id",
        'notebook_id': "previous-notebook-id",
        # ... other context data
    }
    
    # Resume from step 4
    result = agent.resume_workflow(
        context=previous_context,
        from_step=4
    )
    
    print("Workflow resumed and completed")


# Example 4: Without team members (will prompt)
def example_no_team():
    """Run without team members initially."""
    
    agent = RFPAcceleratorAgent(
        gcp_project="gcp-sandpit-intelia"
    )
    
    # Run steps 1-5 without team members
    result = agent.execute_workflow(
        rfp_files=["path/to/rfp.pdf"],
        client_name="Delta Enterprises",
        rfp_title="Security Audit",
        team_members=None,  # Will skip distribution step
        steps_to_run=[1, 2, 3, 4, 5]
    )
    
    print("Setup complete, ready for team member input")


if __name__ == "__main__":
    # Run the basic example
    # Note: Update file paths and details before running
    print("RFP Accelerator Agent - Usage Examples")
    print("=" * 50)
    print("\nSee the function definitions for usage examples.")
    print("\nTo run via CLI:")
    print("  python main.py run -f rfp.pdf -c 'Acme Corp' -t 'Digital Transformation'")
    print("\nTo run interactively:")
    print("  python main.py interactive")
