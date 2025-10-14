from fastapi import FastAPI, Form
from fastapi.middleware.cors import CORSMiddleware
from google import genai
import os
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()

app = FastAPI()

# Allow frontend to access backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Adjust for your frontend
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize Google Gemini client
client = genai.Client(api_key=os.getenv("GOOGLE_API_KEY"))

@app.get("/")
def root():
    return {"message": "FastAPI Writing Tool Backend is running 🚀"}

@app.post("/log")
def log_dummy(message: str = Form(...)):
    print("Frontend log:", message)
    return {"status": "received"}

@app.post("/format")
def format_text(thoughts: str = Form(...)):
    try:
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=f"You are a professional writing assistant. Polish and refine the following text:\n\n{thoughts}"
        )

        polished_output = response.text.strip()

        # Log to console
        print("=== Gemini API Response ===")
        print(polished_output)
        print("==========================")

        formatted = (
            f"📄 Standardized Response\n\n"
            f"🧠 User Thoughts:\n{thoughts}\n\n"
            f"✅ Polished Output:\n{polished_output}"
        )

        return {"formatted": formatted}

    except Exception as e:
        print("Error:", e)
        return {"error": str(e)}
