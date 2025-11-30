# Deploying Your Agent to Users

Once your agent is built and tested in Vertex AI Agent Builder, you need to publish it so your team can use it.

## Option 1: Google Chat (Recommended for Enterprise)
This makes your agent available as a bot in Google Chat, which is the most natural way for enterprise users to interact with it.

### 1. Enable Google Chat Integration
1.  In **Vertex AI Agent Builder**, open your Agent.
2.  Click **Integrations** in the left sidebar.
3.  Find **Google Chat** and click **Connect**.
4.  Select the **Default** environment and click **Start**.

### 2. Configure the Chat App
1.  Go to the [Google Cloud Console > Google Chat API](https://console.cloud.google.com/apis/api/chat.googleapis.com/hangouts-chat).
2.  Click **Configuration** tab.
3.  **App Name:** Enter "RFP Accelerator".
4.  **Avatar URL:** (Optional) Paste a link to a logo.
5.  **Description:** "AI Agent to automate RFP project setup".
6.  **Functionality:** Check **"Receive 1:1 messages"**.
7.  **Connection Settings:**
    *   Select **Dialogflow CX**. (Vertex AI Agents are built on Dialogflow CX).
    *   **Agent:** Select your "RFP Accelerator" agent from the dropdown.
    *   **Environment:** Select "Default".
8.  **Visibility:**
    *   Check **"Join space and group conversations"** if you want it in rooms.
    *   Under **"Who can install"**, select **"Entire domain"** (to let everyone use it) or limit to specific groups for testing.
9.  Click **Save**.

### 2.1 Configure Google Workspace Marketplace SDK (CRITICAL for Visibility)
Even for internal apps, you **must** configure the Marketplace SDK for the app to appear in the search.

1.  Go to **APIs & Services > Enabled APIs & Services**.
2.  Click **+ ENABLE APIS AND SERVICES**.
3.  Search for **"Google Workspace Marketplace SDK"** and click **Enable**.
4.  Once enabled, click **Manage** (or go to it from the dashboard).
5.  Click **App Configuration** in the left sidebar.
    *   **App Integration:** Select **"Chat app"**.
    *   Click **Save**.
6.  Click **Store Listing** in the left sidebar.
    *   **App Name:** "RFP Accelerator".
    *   **Short Description:** "AI Agent for RFPs".
    *   **Detailed Description:** "AI Agent to automate RFP project setup".
    *   **Graphics:** Upload the required icons (you can use placeholders for now).
    *   **Support Information:** Enter your email.
    *   **Installation Settings:** Select **"Private"** (Visible to users in my domain).
    *   Click **Save**.

### 3. Test in Google Chat
1.  Open [Google Chat](https://chat.google.com).
2.  Click **New chat** (+) > **Find apps**.
3.  Search for **"RFP Accelerator"**.
4.  Click **Chat**.
5.  Type: *"Start a new RFP project"* and verify it works!

---

## Option 2: Web Widget (Dialogflow Messenger)
This provides a chat bubble widget that you can embed on any internal website (Intranet, Wiki, SharePoint).

1.  In **Vertex AI Agent Builder**, go to **Integrations**.
2.  Find **Dialogflow Messenger** and click **Connect**.
3.  Click **Enable**.
4.  Copy the provided **HTML Code**.
5.  Paste this code into the `<body>` of your internal website.

Example HTML:
```html
<script src="https://www.gstatic.com/dialogflow-console/fast/messenger/bootstrap.js?v=1"></script>
<df-messenger
  intent="WELCOME"
  chat-title="RFP Accelerator"
  agent-id="[YOUR_AGENT_ID]"
  language-code="en"
></df-messenger>
```

---

## Option 3: Gemini App (gemini.google.com)
*Note: Direct integration into the main Gemini app is currently in Preview/Beta for Enterprise.*

If your organization has access to **Gemini Extensions** for custom agents:
1.  You typically need to wrap your agent as a **Google Workspace Add-on**.
2.  Deploy the Add-on domain-wide.
3.  Users can then invoke it via `@RFP Accelerator` in the Gemini app.

**Recommendation:** Stick to **Google Chat** (Option 1) for now as it is the most stable and widely supported method for Enterprise Agents.
