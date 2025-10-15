from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from google import genai
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

origins = [
     "https://writing-tool-frontend-oam94obeu-karans-projects-eeda5f8d.vercel.app",
    "http://localhost:3000"
]
app = FastAPI()

# CORS – update with your deployed frontend URL
app.add_middleware(
     CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize Gemini client
API_KEY = os.getenv("GOOGLE_API_KEY")
if not API_KEY:
    raise RuntimeError("GOOGLE_API_KEY not set in environment")

client = genai.Client(api_key=API_KEY)


@app.get("/")
def root():
    return {"message": "✅ FastAPI Writing Tool Backend running"}

# Pydantic model for JSON input


class FormatRequest(BaseModel):
    type: str
    preference: str
    key_req: str
    supp_info: str
    extra: str


@app.post("/format")
def format_text(request: FormatRequest):
    type_ = request.type.strip()
    preference = request.preference.strip()
    key_req = request.key_req.strip()
    supp_info = request.supp_info.strip()
    extra = request.extra.strip()

    if not (key_req or supp_info or extra):
        raise HTTPException(status_code=400, detail="Empty text")

    if len(key_req + supp_info + extra) > 2000:
        raise HTTPException(
            status_code=400, detail="Input too long (max 2000 chars)")

    # Determine model names and strength from preference
    preference_map = {
        "Model A Strongly": ("A", "B", "strongly"),
        "Model A Slightly": ("A", "B", "slightly"),
        "Neutral": ("A", "B", "neutral"),
        "Model B Slightly": ("B", "A", "slightly"),
        "Model B Strongly": ("B", "A", "strongly"),
        "Unsure": ("A", "B", "unsure"),
    }
    model, other_model, strength = preference_map.get(
        preference, ("A", "B", "neutral"))

    # Select template based on type
    if type_ == "Process Performance":
        template = (
            f"Model {model} is preferred based on process performance.\n"
            f"In terms of key requirements, {key_req}.\n"
            f"Regarding supplementary information, {supp_info}.\n"
            f"Considering efficiency and errors, {extra}.\n"
            f"Therefore, Model {model} is {strength} better than Model {other_model}.\n\n"
            "Rephrase the text for grammar and clarity only. "
            "Do NOT change structure or format. Do not add or remove information.\n\n"
            "✅ Consistent structure\n✅ Perfect grammar and phrasing\n✅ Human-sounding clarity\n✅ Zero format drift"
        )
    else:  # Outcome Performance
        template = (
            f"Model {model} is preferred based on outcome performance.\n"
            f"In terms of key results, {key_req}.\n"
            f"Regarding supplementary information, {supp_info}.\n"
            f"Additionally, {extra}.\n"
            f"Therefore, Model {model} is {strength} better than Model {other_model}.\n\n"
            "Rephrase the text for grammar and clarity only. "
            "Do NOT change structure or format. Do not add or remove information.\n\n"
            "✅ Consistent structure\n✅ Perfect grammar and phrasing\n✅ Human-sounding clarity\n✅ Zero format drift"
        )

    # Send to Gemini for polishing
    try:
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=f"You are a professional writing assistant. Polish the following text:\n\n{template}"
        )
        print("Gemini response:", response)

        polished = (response.text or "").strip()
        if not polished:
            raise HTTPException(
                status_code=500, detail="Empty response from model")

        return {"formatted": polished}


    except Exception as e:
        print("Gemini API error:", e)
        raise HTTPException(status_code=500, detail="Model error")
