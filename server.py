
import os
import re
from typing import List, Optional
from fastapi import FastAPI, HTTPException, BackgroundTasks
from pydantic import BaseModel
from rfp_agent import RFPAcceleratorAgent
from rfp_agent.integrations.google_drive import GoogleDriveClient

app = FastAPI(title="RFP Accelerator Agent API")

class RFPRequest(BaseModel):
    client_name: str
    rfp_title: str
    rfp_content: Optional[str] = None
    rfp_filename: Optional[str] = None
    rfp_drive_file_id: Optional[str] = None
    team_members: List[str]
    gcp_project: str = "gcp-sandpit-intelia"

def extract_file_id(input_str: str) -> str:
    """Extract file ID from URL or return as is."""
    # Regex for Drive file ID
    match = re.search(r'[-\w]{25,}', input_str)
    return match.group(0) if match else input_str

@app.get("/")
def health_check():
    return {"status": "healthy", "service": "RFP Accelerator Agent"}

@app.post("/run-workflow")
async def run_workflow(request: RFPRequest, background_tasks: BackgroundTasks):
    """
    Trigger the RFP workflow. 
    Accepts either raw content (rfp_content) OR a Google Drive File ID/URL (rfp_drive_file_id).
    """
    temp_files = []
    
    try:
        # Initialize agent
        agent = RFPAcceleratorAgent(
            gcp_project=request.gcp_project,
            config_path="config.yaml"
        )
        
        rfp_files = []
        
        # Scenario 1: Drive File ID provided
        if request.rfp_drive_file_id:
            file_id = extract_file_id(request.rfp_drive_file_id)
            
            # Use the agent's drive client to download
            # Note: We access the private _drive_client or create a new one
            drive_client = GoogleDriveClient(credentials_path=None) # Uses default creds
            
            # Get metadata to determine extension
            metadata = drive_client.get_file_metadata(file_id)
            filename = metadata.get('name', 'rfp_document.pdf')
            temp_path = os.path.abspath(filename)
            
            # Download
            drive_client.download_file(file_id, temp_path)
            rfp_files.append(temp_path)
            temp_files.append(temp_path)
            
        # Scenario 2: Raw Content provided
        elif request.rfp_content:
            # Use provided filename or generate one
            if request.rfp_filename:
                temp_filename = request.rfp_filename
            else:
                temp_filename = f"temp_rfp_{request.client_name.replace(' ', '_')}.txt"
            
            # Ensure we write text content (Gemini extracts text from PDFs)
            with open(temp_filename, "w", encoding="utf-8") as f:
                f.write(request.rfp_content)
            rfp_files.append(os.path.abspath(temp_filename))
            temp_files.append(temp_filename)
            
        else:
            raise HTTPException(status_code=400, detail="Either rfp_content or rfp_drive_file_id must be provided")
        
        # Run workflow
        result = agent.execute_workflow(
            rfp_files=rfp_files,
            client_name=request.client_name,
            rfp_title=request.rfp_title,
            team_members=request.team_members
        )
        
        # Cleanup
        for f in temp_files:
            if os.path.exists(f):
                os.remove(f)
        
        response = {
            "status": "success", 
            "message": "Workflow completed",
            "resources": {
                "folder": result['context'].get('folder_url'),
                "questions": result['context'].get('questions_doc_url'),
                "plan": result['context'].get('plan_doc_url')
            }
        }
        
        # DEBUG: Print the response to logs
        print(f"DEBUG: Tool Response = {response}")
        print(f"DEBUG: Full Context = {result.get('context', {})}")
        
        return response
        
    except Exception as e:
        # Cleanup on error
        for f in temp_files:
            if os.path.exists(f):
                os.remove(f)
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))
