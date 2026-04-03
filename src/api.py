import os
import base64
import json
from pathlib import Path
from fastapi import FastAPI, HTTPException, Header
from pydantic import BaseModel
from google import genai
from google.genai import types
from dotenv import load_dotenv

# 1. Setup Environment
base_dir = Path(__file__).resolve().parent.parent
load_dotenv(base_dir / ".env")

app = FastAPI(title="AI Document Analysis API")

# 2. Configuration
GOOGLE_API_KEY = os.environ.get("GOOGLE_API_KEY")
API_KEY = "sk_track2_987654321"

class DocumentRequest(BaseModel):
    fileName: str
    fileType: str
    fileBase64: str

@app.get("/")
async def root():
    return {"message": "API is running. Access /docs for documentation."}

@app.post("/api/document-analyze")
async def analyze_document(data: DocumentRequest, x_api_key: str = Header(None)):
    # 3. Security Check
    if x_api_key != API_KEY:
        raise HTTPException(status_code=401, detail="Unauthorized")

    if not GOOGLE_API_KEY:
        raise HTTPException(status_code=500, detail="Server Configuration Error: GOOGLE_API_KEY not found.")

    try:
        # 4. Clean and Convert Base64 (Fixes the 422 and 500 errors)
        base64_str = data.fileBase64 
        if "," in base64_str:
            base64_str = base64_str.split(",")[1]
        base64_str = "".join(base64_str.split())
        
        file_bytes = base64.b64decode(base64_str)
        
        # 5. Setup Gemini Client
        client = genai.Client(api_key=GOOGLE_API_KEY)
        
        mime_map = {
            "pdf": "application/pdf",
            "png": "image/png",
            "jpg": "image/jpeg",
            "jpeg": "image/jpeg"
        }
        mime_type = mime_map.get(data.fileType.lower(), "application/octet-stream")
        
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
        
        # 6. Generate Content (Using binary data)
        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=[
                prompt,
                types.Part.from_bytes(data=file_bytes, mime_type=mime_type)
            ],
            config=types.GenerateContentConfig(response_mime_type="application/json")
        )
        
        # 7. Parse and Return
        analysis = json.loads(response.text)
        
        return {
            "status": "success",
            "fileName": data.fileName,
            "summary": analysis.get("summary"),
            "entities": analysis.get("entities"),
            "sentiment": analysis.get("sentiment")
        }

    except Exception as e:
        # This will show you exactly what went wrong in the response body
        return {
            "status": "error",
            "message": str(e)
        }

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run("src.api:app", host="0.0.0.0", port=port, reload=True)
