
import os
from typing import List, Optional
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from rfp_agent.integrations.google_drive import GoogleDriveClient

app = FastAPI(title="RFP Accelerator Agent API")

class RFPRequest(BaseModel):
    client_name: str
    rfp_title: str
    rfp_content: Optional[str] = "Sample RFP content"
    team_members: List[str] = []

class RFPResources(BaseModel):
    folder: str
    questions: str
    plan: str

class RFPResponse(BaseModel):
    status: str
    message: str
    resources: RFPResources

@app.get("/")
def health_check():
    return {"status": "healthy", "service": "RFP Accelerator Agent"}

@app.post("/run-workflow", response_model=RFPResponse)
async def run_workflow(request: RFPRequest):
    """
    Simplified workflow - just creates Drive folder and returns link.
    """
    try:
        print(f"DEBUG: Received request for {request.client_name} - {request.rfp_title}")
        
        # Initialize Google Drive client
        drive_client = GoogleDriveClient()
        
        # Create folder name
        folder_name = f"{request.client_name} - {request.rfp_title}"
        print(f"DEBUG: Creating folder: {folder_name}")
        
        # Create project folder structure
        folder_structure = drive_client.create_project_folder(folder_name)
        
        print(f"DEBUG: Folder created: {folder_structure['main_folder_url']}")
        
        # Share with team members
        if request.team_members:
            print(f"DEBUG: Sharing with {request.team_members}")
            drive_client.share_folder(
                folder_structure['main_folder_id'],
                request.team_members,
                role='writer'
            )
        
        # FALLBACK FOR TESTING: Make public to anyone with link
        # This ensures the user can access it even if email sharing fails
        print("DEBUG: Making folder public for testing...")
        try:
            drive_client.service.permissions().create(
                fileId=folder_structure['main_folder_id'],
                body={'type': 'anyone', 'role': 'reader'},
                fields='id'
            ).execute()
        except Exception as e:
            print(f"WARNING: Failed to make public: {e}")

        # Format the response with URLs in the message so the Agent can't ignore them
        folder_url = folder_structure['main_folder_url']
        analysis_url = folder_structure['subfolders']['analysis']['url']
        planning_url = folder_structure['subfolders']['planning']['url']
        
        message = f"""Project workspace created successfully!

Drive Folder: {folder_url}
Analysis Folder: {analysis_url}
Planning Folder: {planning_url}

IMPORTANT: If you cannot access these links, ensure you provided your email address in the 'team_members' list."""
        
        response = {
            "status": "success", 
            "message": message,
            "resources": {
                "folder": folder_url,
                "questions": analysis_url,
                "plan": planning_url
            }
        }
        
        print(f"DEBUG: Returning response: {response}")
        return response
        
    except Exception as e:
        print(f"ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))
