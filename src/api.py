import os
import json
import base64
from pathlib import Path
from dotenv import load_dotenv
from fastapi import FastAPI, Header, HTTPException
from pydantic import BaseModel
from google import genai
from google.genai import types

# Setup Environment
base_dir = Path(__file__).resolve().parent.parent
load_dotenv(base_dir / ".env")

app = FastAPI(title="AI Document Analysis API")
GOOGLE_API_KEY = os.environ.get("GOOGLE_API_KEY")

class DocumentRequest(BaseModel):
    fileName: str
    fileType: str
    fileBase64: str

@app.get("/")
async def root():
    return {"message": "API is running. Access /docs for documentation."}

@app.post("/api/document-analyze")
async def analyze_document(data: DocumentRequest, x_api_key: str = Header(None)):
    # 1. Security Check
    if x_api_key != "sk_track2_987654321":
        raise HTTPException(status_code=401, detail="Unauthorized")

    if not GOOGLE_API_KEY:
        raise HTTPException(status_code=500, detail="GOOGLE_API_KEY not found in environment.")

    try:
        # 2. CLEAN THE BASE64 STRING (Fixes the 422 Error)
        b64_str = data.fileBase64
        
        # Remove prefix if user pasted 'data:application/pdf;base64,'
        if "," in b64_str:
            b64_str = b64_str.split(",")[1]
            
        # Remove all newlines/spaces that break JSON
        b64_str = "".join(b64_str.split())
        
        # Convert to binary bytes
        file_bytes = base64.b64decode(b64_str)

        # 3. Setup Gemini Client (Using 1.5 Flash for better quota)
        client = genai.Client(api_key=GOOGLE_API_KEY)
        model_id = "gemini-1.5-flash" 
        
        prompt = """
        Analyze this document and return ONLY a JSON object with:
        "summary": a short summary,
        "entities": names, dates, organizations, amounts,
        "sentiment": Positive, Neutral, or Negative.
        """
        
        mime_map = {"pdf": "application/pdf", "png": "image/png", "jpg": "image/jpeg", "jpeg": "image/jpeg"}
        mime_type = mime_map.get(data.fileType.lower(), "application/octet-stream")
        
        # 4. Generate Content
        response = client.models.generate_content(
            model=model_id,
            contents=[
                prompt,
                types.Part.from_bytes(data=file_bytes, mime_type=mime_type)
            ],
            config=types.GenerateContentConfig(response_mime_type="application/json")
        )
        
        # 5. Return Clean JSON
        return {
            "status": "success",
            "fileName": data.fileName,
            "analysis": json.loads(response.text)
        }

    except Exception as e:
        return {"status": "error", "message": str(e)}

if __name__ == "__main__":
    import uvicorn
    # Use string reference to avoid multiprocessing issues on Railway
    port = int(os.environ.get("PORT", 8000)) 
    uvicorn.run("api:app", host="0.0.0.0", port=port, reload=True)
