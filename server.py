
import os
from typing import List, Optional
from fastapi import FastAPI, HTTPException, BackgroundTasks
from pydantic import BaseModel
from rfp_agent import RFPAcceleratorAgent

app = FastAPI(title="RFP Accelerator Agent API")

class RFPRequest(BaseModel):
    client_name: str
    rfp_title: str
    rfp_content: str  # Content of the RFP (since we can't easily upload files to a stateless service)
    team_members: List[str]
    gcp_project: str = "gcp-sandpit-intelia"

@app.get("/")
def health_check():
    return {"status": "healthy", "service": "RFP Accelerator Agent"}

@app.post("/run-workflow")
async def run_workflow(request: RFPRequest, background_tasks: BackgroundTasks):
    """
    Trigger the RFP workflow. 
    Note: In a real production scenario, we would upload files to GCS.
    For this demo, we'll save the content to a temporary file.
    """
    try:
        # Create a temporary file for the RFP content
        temp_filename = f"temp_rfp_{request.client_name.replace(' ', '_')}.txt"
        with open(temp_filename, "w") as f:
            f.write(request.rfp_content)
            
        # Initialize agent
        agent = RFPAcceleratorAgent(
            gcp_project=request.gcp_project,
            config_path="config.yaml" # Will use the container's config
        )
        
        # Run workflow (synchronously for now, but ideally backgrounded)
        # We wrap this in a try/except block to handle the execution
        result = agent.execute_workflow(
            rfp_files=[os.path.abspath(temp_filename)],
            client_name=request.client_name,
            rfp_title=request.rfp_title,
            team_members=request.team_members
        )
        
        # Clean up temp file
        os.remove(temp_filename)
        
        return {
            "status": "success", 
            "message": "Workflow completed",
            "resources": {
                "folder": result['context'].get('folder_url'),
                "questions": result['context'].get('questions_doc_url'),
                "plan": result['context'].get('plan_doc_url')
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))
