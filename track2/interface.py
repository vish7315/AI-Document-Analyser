import streamlit as st
import requests
import base64

st.title("Document Analysis Dashboard")

uploaded_file = st.file_uploader("Upload Document", type=["pdf", "png", "jpg", "jpeg"])

if uploaded_file:
    if st.button("Submit to API"):
        with st.spinner("Communicating with API..."):
            uploaded_file.seek(0) 
            file_bytes = uploaded_file.read()
            
            b64 = base64.b64encode(file_bytes).decode()
            
            payload = {
                "fileName": uploaded_file.name,
                "fileType": uploaded_file.name.split('.')[-1],
                "fileBase64": b64
            }
            headers = {"x-api-key": "sk_track2_987654321"}
            
            try:
                response = requests.post("http://localhost:8000/api/document-analyze", json=payload, headers=headers)
                
                if response.status_code == 200:
                    st.json(response.json()) # Success response [cite: 41-43]
                else:
                    st.error(f"Error {response.status_code}: {response.text}")
            except Exception as e:
                st.error(f"Connection Refused: Is api.py running? {e}")
