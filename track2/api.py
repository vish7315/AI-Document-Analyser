import os
from pathlib import Path
from dotenv import load_dotenv
from fastapi import FastAPI, Header, HTTPException, Request
from google import genai
from google.genai import types
import json
import base64

# --- FIX: ROBUST PATH LOADING ---
# This finds the directory of 'api.py', goes up one level, and looks for '.env'
env_path = Path(__file__).resolve().parent.parent / ".env"
load_dotenv(dotenv_path=env_path)

app = FastAPI()

# Fetch the key from the environment
GOOGLE_API_KEY = os.environ.get("GOOGLE_API_KEY")

@app.post("/api/document-analyze")
async def analyze_document(request: Request, x_api_key: str = Header(None)):
    # 6. API Authentication [cite: 24-26]
    if x_api_key != "sk_track2_987654321":
        raise HTTPException(status_code=401, detail="Unauthorized")

    if not GOOGLE_API_KEY:
        raise HTTPException(
            status_code=500, 
            detail=f"Key Not Found. Looked at: {env_path}"
        )

    try:
        body = await request.json()
        client = genai.Client(api_key=GOOGLE_API_KEY)
        
        # Requirement: AI-powered extraction [cite: 4, 8, 9]
        prompt = """
        Analyze this document and return ONLY a JSON object:
        {
            "summary": "concise summary",
            "entities": {"names": [], "dates": [], "organizations": [], "amounts": []},
            "sentiment": "Positive/Neutral/Negative"
        }
        """
        
        file_data = base64.b64decode(body['fileBase64'])
        # Multi-format support [cite: 6, 20]
        mime = "application/pdf" if body['fileType'] == "pdf" else "image/jpeg"
        
        response = client.models.generate_content(
            model="gemini-3-flash-preview",
            contents=[prompt, types.Part.from_bytes(data=file_data, mime_type=mime)],
            config=types.GenerateContentConfig(response_mime_type="application/json")
        )
        
        # 9. API Response Body (Success) [cite: 41, 44-54]
        analysis = json.loads(response.text)
        return {
            "status": "success",
            "fileName": body.get("fileName"),
            "summary": analysis.get("summary"),
            "entities": analysis.get("entities"),
            "sentiment": analysis.get("sentiment")
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)