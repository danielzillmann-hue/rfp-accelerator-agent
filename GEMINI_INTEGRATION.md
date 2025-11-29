# Integrating RFP Agent with Gemini Enterprise (Vertex AI)

Now that your RFP Agent is running on Cloud Run, you can register it as a **Tool** in Vertex AI Agent Builder. This allows you to invoke the agent through a conversational interface (like a custom Gemini chatbot).

## Step 1: Get your Service URL & OpenAPI Spec

1.  **Find your Service URL:**
    *   Go to [Google Cloud Console > Cloud Run](https://console.cloud.google.com/run).
    *   Click on `rfp-agent-service`.
    *   Copy the URL at the top (e.g., `https://rfp-agent-service-xyz.a.run.app`).

2.  **Get the OpenAPI Specification:**
    *   I have generated the `openapi.json` file locally in your project folder.
    *   **Action:** Download this `openapi.json` file from your project folder to your computer.

## Step 2: Create a Tool in Vertex AI Agent Builder

1.  Go to [Vertex AI Agent Builder](https://console.cloud.google.com/gen-app-builder/engines).
2.  Click **Create App**.
3.  Select **Agent** (Conversational).
4.  Name it "RFP Accelerator" and create it.
5.  In the Agent console, go to **Tools** > **Create**.
6.  **Tool Type:** Select **OpenAPI**.
7.  **Tool Name:** `rfp_creator_tool`.
8.  **Schema:** Upload the `openapi.json` file.
9.  **Authentication:**
    *   **IMPORTANT:** Select **"Service Agent"**.
    *   This allows Vertex AI to securely talk to your private Cloud Run service.
10. Click **Save**.

## Step 3: Configure the Agent Instructions

1.  Go to the **Agent** settings (Instructions).
2.  **Paste these exact instructions:**

    ```text
    You are an RFP Project Manager. Your goal is to help users kick off new RFP projects.
    
    Your primary tool is 'rfp_creator_tool', which creates a project workspace in Google Drive.
    
    When a user provides a Client Name and RFP Title, use the tool to initialize the project.
    
    HANDLING FILE UPLOADS:
    - If the user uploads a file (PDF, DOCX, etc.) in the chat, you must process it.
    - Extract the full text content from the uploaded file.
    - Pass this text content to the 'rfp_content' parameter of the tool.
    - Pass the original filename (or a descriptive name ending in .txt) to the 'rfp_filename' parameter.
    
    Always confirm the Client Name and RFP Title with the user before running the tool.
    
    After the tool runs, provide the links to the created documents and the Drive folder.
    ```

3.  Under **Available Tools**, select your `rfp_creator_tool`.

## Step 4: Test it!

1.  Use the **Preview** chat on the right side.
2.  **Click the Paperclip icon** and upload a sample RFP PDF.
3.  Type: *"Start a project for this RFP for Acme Corp."*
4.  Gemini should:
    *   Read your PDF.
    *   Ask to confirm details.
    *   Call your tool with the file content.
    *   Return the Drive link!

---

## 🔐 Security Note (Service Agent Auth)

Since we selected "Service Agent" authentication, you must ensure the Vertex AI Service Agent has permission to invoke your Cloud Run service.

1.  Go to [Cloud Run](https://console.cloud.google.com/run).
# Integrating RFP Agent with Gemini Enterprise (Vertex AI)

Now that your RFP Agent is running on Cloud Run, you can register it as a **Tool** in Vertex AI Agent Builder. This allows you to invoke the agent through a conversational interface (like a custom Gemini chatbot).

## Step 1: Get your Service URL & OpenAPI Spec

1.  **Find your Service URL:**
    *   Go to [Google Cloud Console > Cloud Run](https://console.cloud.google.com/run).
    *   Click on `rfp-agent-service`.
    *   Copy the URL at the top (e.g., `https://rfp-agent-service-xyz.a.run.app`).

2.  **Get the OpenAPI Specification:**
    *   I have generated the `openapi.json` file locally in your project folder.
    *   **Action:** Download this `openapi.json` file from your project folder to your computer.

## Step 2: Create a Tool in Vertex AI Agent Builder

1.  Go to [Vertex AI Agent Builder](https://console.cloud.google.com/gen-app-builder/engines).
2.  Click **Create App**.
3.  Select **Agent** (Conversational).
4.  Name it "RFP Accelerator" and create it.
5.  In the Agent console, go to **Tools** > **Create**.
6.  **Tool Type:** Select **OpenAPI**.
7.  **Tool Name:** `rfp_creator_tool`.
8.  **Schema:** Upload the `openapi.json` file.
9.  **Authentication:**
    *   **IMPORTANT:** Select **"Service Agent"**.
    *   This allows Vertex AI to securely talk to your private Cloud Run service.
10. Click **Save**.

## Step 3: Configure the Agent Instructions

1.  Go to the **Agent** settings (Instructions).
2.  **Paste these exact instructions:**

    ```text
    You are an RFP Project Manager. Your goal is to help users kick off new RFP projects.
    
    Your primary tool is 'rfp_creator_tool', which creates a project workspace in Google Drive.
    
    When a user provides a Client Name and RFP Title, use the tool to initialize the project.
    
    HANDLING FILE UPLOADS:
    - If the user uploads a file (PDF, DOCX, etc.) in the chat, you must process it.
    - Extract the full text content from the uploaded file.
    - Pass this text content to the 'rfp_content' parameter of the tool.
    - Pass the original filename (or a descriptive name ending in .txt) to the 'rfp_filename' parameter.
    
    Always confirm the Client Name and RFP Title with the user before running the tool.
    
    After the tool runs, provide the links to the created documents and the Drive folder.
    ```

3.  Under **Available Tools**, select your `rfp_creator_tool`.

## Step 4: Test it!

1.  Use the **Preview** chat on the right side.
2.  **Click the Paperclip icon** and upload a sample RFP PDF.
3.  Type: *"Start a project for this RFP for Acme Corp."*
4.  Gemini should:
    *   Read your PDF.
    *   Ask to confirm details.
    *   Call your tool with the file content.
    *   Return the Drive link!

---

## 🔐 Security Note (Service Agent Auth)

Since we selected "Service Agent" authentication, you must ensure the Vertex AI Service Agent has permission to invoke your Cloud Run service.

1.  Go to [Cloud Run](https://console.cloud.google.com/run).
2.  Select `rfp-agent-service`.
3.  Click **Security** tab.
4.  Ensure "Require authentication" is selected.
5.  Go to **Permissions** tab.
6.  Click **Add Principal**.
7.  Enter: `service-[YOUR_PROJECT_NUMBER]@gcp-sa-dialogflow.iam.gserviceaccount.com` (You can find this email in the Vertex AI Agent Builder settings).
8.  Role: **Cloud Run Invoker**.

---

## 📝 Note on NotebookLM

Currently, **NotebookLM does not have a public API**. Therefore, the Agent cannot automatically create the notebook for you.

Instead, the Agent will:
1.  **Create all necessary files** in Google Drive.
2.  **Provide you with a link** to NotebookLM.
3.  **Give you manual instructions** on how to quickly import the Drive folder into a new Notebook.

This is a temporary limitation until Google releases the NotebookLM API.
