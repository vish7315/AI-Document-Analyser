import os
import json
import base64
from pathlib import Path
from dotenv import load_dotenv
from fastapi import FastAPI, Header, HTTPException
from pydantic import BaseModel
from google import genai
from google.genai import types

# 1. Setup Environment
base_dir = Path(__file__).resolve().parent.parent
load_dotenv(base_dir / ".env")

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
    return {"status": "online", "message": "API is running"}

@app.post("/api/document-analyze")
async def analyze_document(data: DocumentRequest, x_api_key: str = Header(None)):
    if x_api_key != API_KEY:
        raise HTTPException(status_code=401, detail="Unauthorized")

    if not GOOGLE_API_KEY:
        raise HTTPException(status_code=500, detail="Server Error: Google API Key missing")

    try:
        # 3. Prepare Data
        b64_str = data.fileBase64
        if "," in b64_str:
            b64_str = b64_str.split(",")[1]
        b64_str = "".join(b64_str.split())
        file_bytes = base64.b64decode(b64_str)

        client = genai.Client(api_key=GOOGLE_API_KEY)
        
        mime_map = {"pdf": "application/pdf", "png": "image/png", "jpg": "image/jpeg", "jpeg": "image/jpeg"}
        mime_type = mime_map.get(data.fileType.lower(), "application/octet-stream")

        prompt = """Analyze this document and return ONLY a JSON object:
        {"summary": "...", "entities": {"names":[], "dates":[], "organizations":[], "amounts":[]}, "sentiment": "..."}"""

        # 4. Multi-Model Fallback Logic (Prevents Crashing)
        # We try the newest 2.0 model first, fall back to 1.5 if busy
        models_to_try = ["gemini-2.0-flash","gemini-3-flash-preview", "gemini-1.5-flash"]
        last_error = ""

        for model_id in models_to_try:
            try:
                response = client.models.generate_content(
                    model=model_id,
                    contents=[prompt, types.Part.from_bytes(data=file_bytes, mime_type=mime_type)],
                    config=types.GenerateContentConfig(response_mime_type="application/json")
                )
                
                # If successful, parse and return immediately
                analysis_result = json.loads(response.text)
                return {
                    "status": "success",
                    "fileName": data.fileName,
                    "summary": analysis_result.get("summary"),
                    "entities": analysis_result.get("entities"),
                    "sentiment": analysis_result.get("sentiment"),
                    "engine": model_id  # Optional: helps you see which model was used
                }
            except Exception as e:
                last_error = str(e)
                continue # Try the next model in the list

        # If all models fail
        return {"status": "error", "message": f"All models exhausted. Last error: {last_error}"}

    except Exception as e:
        return {"status": "error", "message": str(e)}

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run("src.api:app", host="0.0.0.0", port=port, reload=True)
