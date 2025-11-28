
import json
from fastapi.openapi.utils import get_openapi
from server import app

# Generate the OpenAPI schema with explicit 3.0.2 version
openapi_schema = get_openapi(
    title=app.title,
    version=app.version,
    openapi_version="3.0.2",  # Force 3.0.x for Vertex AI compatibility
    routes=app.routes,
)

# Save to file
with open("openapi.json", "w") as f:
    json.dump(openapi_schema, f, indent=2)

print("✅ openapi.json (v3.0.2) generated successfully!")
