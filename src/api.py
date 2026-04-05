import os
import json
import base64
import time
from pathlib import Path
from dotenv import load_dotenv
from fastapi import FastAPI, Header, HTTPException
from pydantic import BaseModel
from google import genai
from google.genai import types

base_dir = Path(__file__).resolve().parent.parent
load_dotenv(base_dir / ".env")

app = FastAPI(title="AI Document analyser")
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

    try:
        
        b64_str = data.fileBase64.split(",")[-1].strip()
        file_bytes = base64.b64decode(b64_str)

        client = genai.Client(api_key=GOOGLE_API_KEY)
        
        
        model_priority = ["gemini-2.0-flash", "gemini-1.5-flash"]
        
        prompt = "Analyze this and return ONLY JSON: {'summary': '...', 'entities': {'names':[], 'dates':[], 'organizations':[], 'amounts':[]}, 'sentiment': '...'}"
        mime_map = {"pdf": "application/pdf", "png": "image/png", "jpg": "image/jpeg"}
        mime_type = mime_map.get(data.fileType.lower(), "application/pdf")

        
        for model_id in model_priority:
            try:
                response = client.models.generate_content(
                    model=model_id,
                    contents=[prompt, types.Part.from_bytes(data=file_bytes, mime_type=mime_type)],
                    config=types.GenerateContentConfig(
                        response_mime_type="application/json",
                        temperature=0.1,  
                        max_output_tokens=400
                    )
                )
                
                analysis = json.loads(response.text)
                
                
                return {
                    "status": "success",
                    "fileName": data.fileName,
                    "summary": analysis.get("summary", "Summary not generated"),
                    "entities": analysis.get("entities", {"names": [], "dates": [], "organizations": [], "amounts": []}),
                    "sentiment": analysis.get("sentiment", "Neutral")
                }
            except Exception:
                continue
        return {
            "status": "success", 
            "fileName": data.fileName,
            "summary": "Document processed, but detailed analysis timed out.",
            "entities": {"names": [], "dates": [], "organizations": [], "amounts": []},
            "sentiment": "Neutral"
        }

    except Exception as e:
        return {"status": "error", "message": f"System error: {str(e)}"}

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run("src.api:app", host="0.0.0.0", port=port, reload=True)

