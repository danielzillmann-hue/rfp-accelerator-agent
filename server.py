import os
import re
import tempfile
from typing import List, Optional
from fastapi import FastAPI, HTTPException, BackgroundTasks, Request, Form, UploadFile, File
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from rfp_agent import RFPAcceleratorAgent
from rfp_agent.integrations.google_drive import GoogleDriveClient

app = FastAPI(title="RFP Accelerator Agent API")
templates = Jinja2Templates(directory="templates")

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

@app.get("/ui", response_class=HTMLResponse)
async def ui_home(request: Request):
    """Render the main HTML interface for the RFP Accelerator Agent."""
    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "result": None,
            "error": None,
        },
    )

def _execute_workflow(rfp_files: List[str], client_name: str, rfp_title: str, team_members: List[str], gcp_project: str):
    """Run the core RFP workflow and format the standard response."""
    agent = RFPAcceleratorAgent(
        gcp_project=gcp_project,
        config_path="config.yaml",
    )

    result = agent.execute_workflow(
        rfp_files=rfp_files,
        client_name=client_name,
        rfp_title=rfp_title,
        team_members=team_members,
    )

    response = {
        "status": "success",
        "message": "Workflow completed",
        "resources": {
            "folder": result["context"].get("folder_url"),
            "questions": result["context"].get("questions_doc_url"),
            "plan": result["context"].get("plan_doc_url"),
        },
    }

    # DEBUG: Print the response to logs
    print(f"DEBUG: Tool Response = {response}")
    print(f"DEBUG: Full Context = {result.get('context', {})}")

    return response


@app.post("/run-workflow")
async def run_workflow(request: RFPRequest, background_tasks: BackgroundTasks):
    """
    Trigger the RFP workflow via JSON API.
    Accepts either raw content (rfp_content) OR a Google Drive File ID/URL (rfp_drive_file_id).
    """
    temp_files: List[str] = []

    try:
        rfp_files: List[str] = []

        # Scenario 1: Drive File ID provided
        if request.rfp_drive_file_id:
            file_id = extract_file_id(request.rfp_drive_file_id)

            drive_client = GoogleDriveClient(credentials_path=None)  # Uses default creds

            metadata = drive_client.get_file_metadata(file_id)
            filename = metadata.get("name", "rfp_document.pdf")
            temp_path = os.path.abspath(filename)

            drive_client.download_file(file_id, temp_path)
            rfp_files.append(temp_path)
            temp_files.append(temp_path)

        # Scenario 2: Raw Content provided
        elif request.rfp_content:
            if request.rfp_filename:
                temp_filename = request.rfp_filename
            else:
                temp_filename = f"temp_rfp_{request.client_name.replace(' ', '_')}.txt"

            with open(temp_filename, "w", encoding="utf-8") as f:
                f.write(request.rfp_content)
            abs_path = os.path.abspath(temp_filename)
            rfp_files.append(abs_path)
            temp_files.append(abs_path)

        else:
            raise HTTPException(
                status_code=400,
                detail="Either rfp_content or rfp_drive_file_id must be provided",
            )

        response = _execute_workflow(
            rfp_files=rfp_files,
            client_name=request.client_name,
            rfp_title=request.rfp_title,
            team_members=request.team_members,
            gcp_project=request.gcp_project,
        )

        return response

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    finally:
        for f in temp_files:
            if os.path.exists(f):
                os.remove(f)

@app.post("/ui/run-workflow", response_class=HTMLResponse)
async def run_workflow_form(
    request: Request,
    client_name: str = Form(...),
    rfp_title: str = Form(...),
    rfp_content: Optional[str] = Form(None),
    rfp_drive_file_id: Optional[str] = Form(None),
    rfp_files: Optional[List[UploadFile]] = File(None),
    team_members: Optional[str] = Form(None),
    gcp_project: str = Form("gcp-sandpit-intelia"),
):
    """HTML form handler that triggers the RFP workflow and renders results."""
    try:
        # Parse team members from comma/space separated string
        team_list: List[str] = []
        if team_members:
            raw_items = [item.strip() for item in team_members.replace(";", ",").split(",")]
            team_list = [item for item in raw_items if item]

        temp_files: List[str] = []
        rfp_file_paths: List[str] = []

        # Handle uploaded files (one or many)
        if rfp_files:
            for upload in rfp_files:
                if not upload.filename:
                    continue
                suffix = os.path.splitext(upload.filename)[1]
                fd, temp_path = tempfile.mkstemp(suffix=suffix or "")
                os.close(fd)
                with open(temp_path, "wb") as out_f:
                    out_f.write(await upload.read())
                rfp_file_paths.append(temp_path)
                temp_files.append(temp_path)

        # Optional: also support Drive URL/ID or inline content, same as JSON API
        if rfp_drive_file_id:
            file_id = extract_file_id(rfp_drive_file_id)
            drive_client = GoogleDriveClient(credentials_path=None)
            metadata = drive_client.get_file_metadata(file_id)
            filename = metadata.get("name", "rfp_document.pdf")
            temp_path = os.path.abspath(filename)
            drive_client.download_file(file_id, temp_path)
            rfp_file_paths.append(temp_path)
            temp_files.append(temp_path)
        elif rfp_content and not rfp_file_paths:
            # Fallback to text content if no files uploaded
            temp_filename = f"temp_rfp_{client_name.replace(' ', '_')}.txt"
            with open(temp_filename, "w", encoding="utf-8") as f:
                f.write(rfp_content)
            abs_path = os.path.abspath(temp_filename)
            rfp_file_paths.append(abs_path)
            temp_files.append(abs_path)

        if not rfp_file_paths:
            raise HTTPException(
                status_code=400,
                detail="Please upload at least one RFP document, provide inline content, or a Drive file URL/ID.",
            )

        result = _execute_workflow(
            rfp_files=rfp_file_paths,
            client_name=client_name,
            rfp_title=rfp_title,
            team_members=team_list,
            gcp_project=gcp_project,
        )

        return templates.TemplateResponse(
            "index.html",
            {
                "request": request,
                "result": result,
                "error": None,
            },
        )
    except HTTPException as exc:
        return templates.TemplateResponse(
            "index.html",
            {
                "request": request,
                "result": None,
                "error": exc.detail,
            },
        )
    finally:
        if "temp_files" in locals():
            for f in temp_files:
                if os.path.exists(f):
                    os.remove(f)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))
