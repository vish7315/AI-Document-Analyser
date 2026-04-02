# 📑 AI-Powered Document Analysis System (Track 2)

An enterprise-grade REST API developed for the **HCL AI Impact Buildathon**. This system leverages the cutting-edge **Google Gemini 3 Flash** model to perform high-speed, multimodal document summarization, entity extraction, and sentiment analysis.

---

## 🚀 Live Deployment
* **API Endpoint:** `https://web-production-bb0cf.up.railway.app/api/document-analyze`
* **Interactive API Tester (Swagger UI):** [https://web-production-bb0cf.up.railway.app/docs](https://web-production-bb0cf.up.railway.app/docs)

---

## 🧠 AI Capabilities (Powered by Gemini 3 Flash)
By utilizing the **Gemini 3 Flash** (`gemini-3-flash-preview`) model, this system provides:
* **Multimodal Native Processing:** Direct analysis of PDF and Image layouts without the need for external OCR (Optical Character Recognition) tools.
* **Intelligent Summarization:** Generates context-aware 3-bullet point summaries of complex documents.
* **Named Entity Recognition (NER):** High-accuracy extraction of Names, Dates, Organizations, and Monetary values.
* **Sentiment Classification:** Automated tone analysis (Positive, Neutral, Negative) for document categorization.

---

## ✨ Core Features
* **Secure Authentication:** Mandatory `x-api-key` validation (`sk_track2_987654321`) as per hackathon requirements.
* **Base64 Integration:** Handles document uploads via standard Base64 encoding for secure, serverless-friendly transmission.
* **FastAPI Framework:** High-performance, asynchronous Python backend for low-latency responses.
* **Cloud Hosted:** Fully deployed on **Railway** with automated SSL (HTTPS) and port management.

---

## 💻 Localhost Setup & Installation

To run this project on your local machine for development or testing, follow these steps:

### 1. Prerequisites
* Python 3.10 or higher installed.
* A Google Gemini API Key (Get one at [aistudio.google.com](https://aistudio.google.com/)).

### 2. Clone and Install
```bash
# Clone the repository
git clone [https://github.com/vish7315/AI-Document-Analyser.git](https://github.com/vish7315/AI-Document-Analyser.git)
cd AI-Document-Analyser

# Create a virtual environment (Recommended)
python -m venv venv

# Activate Virtual Environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Install required dependencies
pip install -r requirements.txt
