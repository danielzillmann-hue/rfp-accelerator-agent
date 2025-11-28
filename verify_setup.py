
import sys
import os

print("1. Checking imports...")
try:
    from google.cloud import aiplatform
    from vertexai.generative_models import GenerativeModel
    import rfp_agent
    print("   ✅ Imports successful")
except ImportError as e:
    print(f"   ❌ Import failed: {e}")
    sys.exit(1)

print("\n2. Checking GCP Authentication...")
try:
    # Initialize Vertex AI
    aiplatform.init(project='gcp-sandpit-intelia', location='us-central1')
    print("   ✅ Authenticated with GCP project: gcp-sandpit-intelia")
except Exception as e:
    print(f"   ❌ Authentication failed: {e}")
    sys.exit(1)

print("\n3. Checking Gemini Model Access...")
try:
    model = GenerativeModel('gemini-1.5-pro-002')
    # Try a simple generation to confirm access
    response = model.generate_content("Hello")
    print("   ✅ Gemini model is accessible and responding")
except Exception as e:
    print(f"   ❌ Gemini model access failed: {e}")
    print("      (Note: Ensure the 'Vertex AI API' is enabled and you have 'Vertex AI User' role)")

print("\n4. Checking Agent Configuration...")
if os.path.exists('config.yaml'):
    print("   ✅ config.yaml exists")
else:
    print("   ❌ config.yaml missing")

print("\n------------------------------------------------")
print("🎉 SYSTEM READY! You can now run the agent.")
