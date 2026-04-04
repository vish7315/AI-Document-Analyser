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

app = FastAPI(title="AI Document analyser")

# 2. Configuration
GOOGLE_API_KEY = os.environ.get("GOOGLE_API_KEY")
# This matches the key you entered in the HCL/GUVI tester
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
    # 3. Security Validation
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
        
        # 5. Binary Conversion
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
        Analyze this document and return ONLY a JSON object:
        {
            "summary": "a short summary",
            "entities": {
                "names": [],
                "dates": [],
                "organizations": [],
                "amounts": []
            },
            "sentiment": "Positive, Neutral, or Negative"
        }
        """

        # 8. Enhanced Detection via Gemini 3 Flash Preview
        response = client.models.generate_content(
            model="gemini-1.5-flash",
            contents=[
                prompt,
                types.Part.from_bytes(data=file_bytes, mime_type=mime_type)
            ],
            config=types.GenerateContentConfig(response_mime_type="application/json")
        )

        # 9. Parse Response Text into a Dictionary
        analysis_result = json.loads(response.text)

        # 10. Flattened Return (Required to pass HCL/GUVI Tester)
        return {
            "status": "success",
            "fileName": data.fileName,
            "summary": analysis_result.get("summary"),
            "entities": analysis_result.get("entities"),
            "sentiment": analysis_result.get("sentiment")
        }

    except Exception as e:
        return {"status": "error", "message": str(e)}

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    # String reference 'src.api:app' is recommended for Railway/Uvicorn
    uvicorn.run("src.api:app", host="0.0.0.0", port=port, reload=True)
