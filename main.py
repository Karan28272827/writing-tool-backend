from fastapi import FastAPI, Form
from fastapi.middleware.cors import CORSMiddleware
from openai import OpenAI
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

# Initialize OpenAI client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

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
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a professional writing assistant that rewrites user thoughts into clean, polished, and natural English."},
                {"role": "user", "content": thoughts}
            ],
            temperature=0.7,
        )

        polished_output = response.choices[0].message.content.strip()

        # Log to console
        print("=== OpenAI API Response ===")
        print(polished_output)
        print("==========================")

        formatted = (
            f"📄 Standardized Response\n\n"
            f"🧠 User Thoughts:\n{thoughts}\n\n"
            f"✅ Polished Output:\n{polished_output}"
        )

        return {"formatted": formatted}

    except Exception as e:
        print("Error:", e)  # Also log errors
        return {"error": str(e)}
