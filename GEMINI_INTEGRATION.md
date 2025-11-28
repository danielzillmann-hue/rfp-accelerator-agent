# Integrating RFP Agent with Gemini Enterprise (Vertex AI)

Now that your RFP Agent is running on Cloud Run, you can register it as a **Tool** in Vertex AI Agent Builder. This allows you to invoke the agent through a conversational interface (like a custom Gemini chatbot).

## Step 1: Get your Service URL & OpenAPI Spec

1.  **Find your Service URL:**
    *   Go to [Google Cloud Console > Cloud Run](https://console.cloud.google.com/run).
    *   Click on `rfp-agent-service`.
    *   Copy the URL at the top (e.g., `https://rfp-agent-service-xyz.a.run.app`).

2.  **Download the OpenAPI Specification:**
    *   Your agent automatically generates this.
    *   Open your browser to: `YOUR_SERVICE_URL/openapi.json`
    *   Save this file as `openapi.json`.

## Step 2: Create a Tool in Vertex AI Agent Builder

1.  Go to [Vertex AI Agent Builder](https://console.cloud.google.com/gen-app-builder/engines).
2.  Click **Create App**.
3.  Select **Agent** (Conversational).
4.  Name it "RFP Accelerator" and create it.
5.  In the Agent console, go to **Tools** > **Create**.
6.  **Tool Type:** Select **OpenAPI**.
7.  **Tool Name:** `rfp_creator_tool`.
8.  **Schema:** Upload the `openapi.json` file you downloaded.
9.  **Authentication:**
    *   If you deployed with `--allow-unauthenticated`, select "Anonymous".
    *   Otherwise, select "Service Agent" (recommended for internal tools).
10. Click **Save**.

## Step 3: Configure the Agent Instructions

1.  Go to the **Agent** settings (Instructions).
2.  Add instructions like this:
    > You are an RFP Project Manager. Your goal is to help users kick off new RFP projects.
    > When a user provides a Client Name and RFP Title, use the 'rfp_creator_tool' to initialize the project.
    > Always confirm the details with the user before running the tool.
    > After the tool runs, provide the links to the created documents.

3.  Under **Available Tools**, select your `rfp_creator_tool`.

## Step 4: Test it!

1.  Use the **Preview** chat on the right side.
2.  Type: *"I have a new RFP for Acme Corp called Digital Transformation."*
3.  Gemini should recognize the intent and ask to confirm.
4.  Say *"Yes, go ahead."*
5.  Gemini will call your Cloud Run API, execute the 7-step workflow, and return the links to the Google Drive folder and Docs!

---

## 🔐 Security Note (Service Agent Auth)

If you want to secure your Cloud Run service (so only Gemini can call it):

1.  Remove `--allow-unauthenticated` from your deployment (edit `deploy.yml`).
2.  In Vertex AI Tool setup, choose **Service Agent** authentication.
3.  Grant the **Vertex AI Service Agent** account the `Cloud Run Invoker` role on your Cloud Run service.
