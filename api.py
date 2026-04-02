import os
import json
import base64
from pathlib import Path
from dotenv import load_dotenv
from fastapi import FastAPI, Header, HTTPException, Request
from pydantic import BaseModel
from google import genai
from google.genai import types

base_dir = Path(__file__).resolve().parent.parent
load_dotenv(base_dir / ".env")

app = FastAPI(title="AI Document Analysis API")
GOOGLE_API_KEY = os.environ.get("GOOGLE_API_KEY")

class DocumentRequest(BaseModel):
    fileName: str
    fileType: str
    fileBase64: str

@app.post("/api/document-analyze")
async def analyze_document(data: DocumentRequest, x_api_key: str = Header(None)):
    
    if x_api_key != "sk_track2_987654321":
        raise HTTPException(status_code=401, detail="Unauthorized")

    if not GOOGLE_API_KEY:
        raise HTTPException(
            status_code=500, 
            detail="Server Configuration Error: GOOGLE_API_KEY not found."
        )

    try:
        client = genai.Client(api_key=GOOGLE_API_KEY)
        
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
        
        file_bytes = base64.b64decode(data.fileBase64)
        
        mime_map = {
            "pdf": "application/pdf",
            "png": "image/png",
            "jpg": "image/jpeg",
            "jpeg": "image/jpeg"
        }
        mime_type = mime_map.get(data.fileType.lower(), "application/octet-stream")
        
        doc_part = types.Part.from_bytes(data=file_bytes, mime_type=mime_type)
        
        response = client.models.generate_content(
            model="gemini-3-flash-preview",
            contents=[prompt, doc_part],
            config=types.GenerateContentConfig(response_mime_type="application/json")
        )
        
        analysis = json.loads(response.text)
        
        return {
            "status": "success",
            "fileName": data.fileName,
            "summary": analysis.get("summary"),
            "entities": analysis.get("entities"),
            "sentiment": analysis.get("sentiment")
        }

    except Exception as e:
        return {
            "status": "error",
            "message": str(e)
        }

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
