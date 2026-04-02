import os
import json
import base64
from pathlib import Path
from dotenv import load_dotenv
from fastapi import FastAPI, Header, HTTPException, Request
from pydantic import BaseModel
from google import genai
from google.genai import types

# --- 1. CONFIGURATION & SECRETS ---
# Dynamically find the .env in the root directory [cite: 59]
base_dir = Path(__file__).resolve().parent.parent
load_dotenv(base_dir / ".env")

app = FastAPI(title="AI Document Analysis API")
GOOGLE_API_KEY = os.environ.get("GOOGLE_API_KEY")

# --- 2. REQUEST SCHEMA ---
# This ensures the 'Request Body' appears in the /docs UI [cite: 39, 40]
class DocumentRequest(BaseModel):
    fileName: str
    fileType: str
    fileBase64: str

# --- 3. API ENDPOINT ---
@app.post("/api/document-analyze")
async def analyze_document(data: DocumentRequest, x_api_key: str = Header(None)):
    
    # 6. API Authentication [cite: 24, 25, 26]
    # Requests without a valid API key must be rejected with 401
    if x_api_key != "sk_track2_987654321":
        raise HTTPException(status_code=401, detail="Unauthorized")

    if not GOOGLE_API_KEY:
        raise HTTPException(
            status_code=500, 
            detail="Server Configuration Error: GOOGLE_API_KEY not found."
        )

    try:
        # Initialize Gemini Client
        client = genai.Client(api_key=GOOGLE_API_KEY)
        
        # 1. Problem Statement Requirements [cite: 3, 4, 8, 9]
        # Leveraging AI to understand structure and extract key info
        prompt = """
        Analyze this document and return ONLY a JSON object:
        {
            "summary": "Provide a concise and accurate summary",
            "entities": {
                "names": ["Extract people's names"],
                "dates": ["Extract relevant dates"],
                "organizations": ["Extract organizations/companies"],
                "amounts": ["Extract monetary amounts"]
            },
            "sentiment": "Classify overall sentiment as Positive, Neutral, or Negative"
        }
        """
        
        # Decode the Base64 document [cite: 21]
        file_bytes = base64.b64decode(data.fileBase64)
        
        # Handle multi-format support: PDF, DOCX, or Image [cite: 6, 20]
        mime_map = {
            "pdf": "application/pdf",
            "png": "image/png",
            "jpg": "image/jpeg",
            "jpeg": "image/jpeg"
        }
        mime_type = mime_map.get(data.fileType.lower(), "application/octet-stream")
        
        doc_part = types.Part.from_bytes(data=file_bytes, mime_type=mime_type)
        
        # Generate AI Analysis using Gemini 3 Flash
        response = client.models.generate_content(
            model="gemini-3-flash-preview",
            contents=[prompt, doc_part],
            config=types.GenerateContentConfig(response_mime_type="application/json")
        )
        
        # Parse the AI response
        analysis = json.loads(response.text)
        
        # 9. API Response Body (Success) [cite: 41, 44, 46, 47, 53]
        return {
            "status": "success",
            "fileName": data.fileName,
            "summary": analysis.get("summary"),
            "entities": analysis.get("entities"),
            "sentiment": analysis.get("sentiment")
        }

    except Exception as e:
        # 10. Response Field Explanation (Error) [cite: 56]
        return {
            "status": "error",
            "message": str(e)
        }

# --- 4. EXECUTION ---
if __name__ == "__main__":
    import uvicorn
    # Use 127.0.0.1 for local browser access to /docs
    # Use 0.0.0.0 for Railway deployment [cite: 15]
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)