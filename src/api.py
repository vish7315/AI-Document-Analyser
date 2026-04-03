import os
import json
import base64
from pathlib import Path
from dotenv import load_dotenv
from fastapi import FastAPI, Header, HTTPException
from pydantic import BaseModel
from google import genai
from google.genai import types

# 1. Setup Environment & App
base_dir = Path(__file__).resolve().parent.parent
load_dotenv(base_dir / ".env")

# Title changed to 'AI Document analyser'
app = FastAPI(title="AI Document analyser")

# 2. Configuration
GOOGLE_API_KEY = os.environ.get("GOOGLE_API_KEY")
API_KEY = "sk_track2_987654321"

class DocumentRequest(BaseModel):
    fileName: str
    fileType: str
    fileBase64: str

@app.get("/")
async def health_check():
    # Message changed to 'API is running'
    return {"status": "online", "message": "API is running"}

@app.post("/api/document-analyze")
async def analyze_document(data: DocumentRequest, x_api_key: str = Header(None)):
    # 3. Security & Config Validation
    if x_api_key != API_KEY:
        raise HTTPException(status_code=401, detail="Unauthorized")

    if not GOOGLE_API_KEY:
        raise HTTPException(status_code=500, detail="Server Error: Google API Key missing")

    try:
        # 4. Data Scrubbing (Fixes 422 Unprocessable Entity)
        b64_str = data.fileBase64
        if "," in b64_str:
            b64_str = b64_str.split(",")[1]
        b64_str = "".join(b64_str.split())
        
        # 5. Binary Conversion (Fixes 500 TypeError)
        file_bytes = base64.b64decode(b64_str)

        # 6. Initialize Gemini Client
        client = genai.Client(api_key=GOOGLE_API_KEY)
        
        mime_map = {
            "pdf": "application/pdf",
            "png": "image/png",
            "jpg": "image/jpeg",
            "jpeg": "image/jpeg"
        }
        mime_type = mime_map.get(data.fileType.lower(), "application/octet-stream")

        # 7. AI Extraction Prompt
        prompt = """
        Act as a document intelligence expert. Analyze this file and return ONLY a JSON object:
        {
            "summary": "3-sentence concise overview",
            "entities": {
                "names": ["People mentioned"],
                "dates": ["Key dates found"],
                "organizations": ["Companies or institutions"],
                "amounts": ["Currency values"]
            },
            "sentiment": "Positive, Neutral, or Negative"
        }
        """

        # 8. Enhanced Detection via Gemini API
        response = client.models.generate_content(
            model="gemini-3-flash-preview",
            contents=[
                prompt,
                types.Part.from_bytes(data=file_bytes, mime_type=mime_type)
            ],
            config=types.GenerateContentConfig(response_mime_type="application/json")
        )

        # 9. Parse and Return
        return {
            "status": "success",
            "fileName": data.fileName,
            "analysis": json.loads(response.text)
        }

    except Exception as e:
        return {"status": "error", "message": str(e)}

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run("src.api:app", host="0.0.0.0", port=port, reload=True)
