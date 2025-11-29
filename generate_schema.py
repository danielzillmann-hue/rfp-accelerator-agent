
import json
from fastapi.openapi.utils import get_openapi
from server import app

def fix_openapi_spec(schema):
    """
    Recursively fix OpenAPI 3.0 compatibility issues.
    Vertex AI doesn't like 'type': 'null' or 'anyOf' with null.
    It prefers 'nullable': true.
    """
    if isinstance(schema, dict):
        # Fix "anyOf": [{"type": "string"}, {"type": "null"}] -> "type": "string", "nullable": true
        if "anyOf" in schema:
            types = schema["anyOf"]
            if len(types) == 2:
                null_type = next((t for t in types if t.get("type") == "null"), None)
                other_type = next((t for t in types if t.get("type") != "null"), None)
                
                if null_type and other_type:
                    schema.pop("anyOf")
                    schema.update(other_type)
                    schema["nullable"] = True
        
        # Fix simple "type": "null" (rare but possible)
        if schema.get("type") == "null":
            schema.pop("type")
            schema["nullable"] = True
            
        for key, value in schema.items():
            fix_openapi_spec(value)
            
    elif isinstance(schema, list):
        for item in schema:
            fix_openapi_spec(item)

# Generate the OpenAPI schema with explicit 3.0.2 version
openapi_schema = get_openapi(
    title=app.title,
    version=app.version,
    openapi_version="3.0.2",  # Force 3.0.x for Vertex AI compatibility
    routes=app.routes,
)

# Apply fixes
fix_openapi_spec(openapi_schema)

# Save to file
with open("openapi.json", "w") as f:
    json.dump(openapi_schema, f, indent=2)

print("✅ openapi.json (v3.0.2) generated successfully with null-type fixes!")
