
import json
from fastapi.openapi.utils import get_openapi
from server_simple import app

# Generate the OpenAPI schema
openapi_schema = get_openapi(
    title=app.title,
    version="1.0.0",
    openapi_version="3.0.2",
    routes=app.routes,
)

# Add the servers section with the Cloud Run URL
openapi_schema["servers"] = [
    {
        "url": "https://rfp-agent-service-566828750593.us-central1.run.app",
        "description": "Production Cloud Run Service"
    }
]

# Save to file
with open("openapi.json", "w") as f:
    json.dump(openapi_schema, f, indent=2)

print("✅ openapi.json generated for simplified server!")
