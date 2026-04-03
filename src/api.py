import os
import base64
from fastapi import FastAPI, HTTPException, Header
from pydantic import BaseModel
from google import genai
from dotenv import load_dotenv

# Initialize the app
load_dotenv()
app = FastAPI(title="HCL AI Impact Buildathon - Track 2")


API_KEY = "sk_track2_987654321"
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")


client = genai.Client(api_key=GOOGLE_API_KEY)

class DocumentRequest(BaseModel):
    fileName: str
    fileType: str
    fileBase64: str

@app.get("/")
async def root():
    return {"message": "API is running. Access /docs for documentation."}

@app.post("/api/document-analyze")
async def analyze_document(request: DocumentRequest, x_api_key: str = Header(None)):
    
    if x_api_key != API_KEY:
        raise HTTPException(status_code=401, detail="Invalid API Key")

   
    raw_data = request.fileBase64
    
   
    if "," in raw_data:
        raw_data = raw_data.split(",")[1]
    
    
    clean_base64 = "".join(raw_data.split())

    try:
        raw_data = request.fileBase64
        if "," in raw_data:
            raw_data = raw_data.split(",")[1]
            
        clean_base64 = "".join(raw_data.split())

        decoded_bytes = base64.b64decode(clean_base64)
        mime_type = "application/pdf" if request.fileType.lower() == "pdf" else "image/jpeg"
        
        prompt = """
        Analyze the attached document and provide:
        1. A concise 3-bullet point summary.
        2. Extract key entities (Names, Dates, Organizations, Amounts).
        3. Determine the sentiment (Positive, Neutral, or Negative).
        Return the result in clear JSON format.
        """

        response = client.models.generate_content(
            model="gemini-1.5-flash", # Use "gemini-1.5-flash" or "gemini-2.0-flash"
            contents=[
                prompt,
                {"mime_type": mime_type, "data": clean_base64}
            ]
        )

        return {
            "status": "success",
            "fileName": request.fileName,
            "analysis": response.text
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    # Note: Using string reference "src.api:app" for local reliability
    uvicorn.run("src.api:app", host="0.0.0.0", port=port, reload=True)
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
    base64_str = request.fileBase64
    if "," in base64_str:
        base64_str = base64_str.split(",")[1]
    base64_str = "".join(base64_str.split())
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
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run("src.api:app", host="0.0.0.0", port=port, reload=True)
