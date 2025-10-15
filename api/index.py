from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from google import genai
import os
import re
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = FastAPI()

# CORS configuration - Get allowed origins from environment
ALLOWED_ORIGINS = os.getenv("ALLOWED_ORIGINS").split(",")
# print(ALLOWED_ORIGINS)
app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
)

# Initialize Gemini client
API_KEY = os.getenv("GOOGLE_API_KEY")
if not API_KEY:
    print("Warning: GOOGLE_API_KEY not set in environment")
    client = None
else:
    client = genai.Client(api_key=API_KEY)


@app.get("/")
def root():
    return {"message": "✅ FastAPI Writing Tool Backend running"}


@app.options("/{path:path}")
async def options_handler(request: Request, path: str):
    return JSONResponse(content={"message": "OK"})


class FormatRequest(BaseModel):
    type: str
    preference: str
    key_req: str
    supp_info: str
    extra: str


@app.post("/format")
async def format_text(request: FormatRequest):
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
    # preference_map = {
    #     "Model A Strongly": ("A", "B", "strongly"),
    #     "Model A Slightly": ("A", "B", "slightly"),
    #     "Neutral": ("A", "B", "neutral"),
    #     "Model B Slightly": ("B", "A", "slightly"),
    #     "Model B Strongly": ("B", "A", "strongly"),
    #     "Unsure": ("A", "B", "unsure"),
    # }
    # model, other_model, strength = preference_map.get(
    #     preference, ("A", "B", "neutral"))

    # # Select template based on type
    # if type_ == "Process Performance":
    #     template = (
    #         f"Model {model} is preferred based on process performance.\n"
    #         f"In terms of key requirements, {key_req}.\n"
    #         f"Regarding supplementary information, {supp_info}.\n"
    #         f"Considering efficiency and errors, {extra}.\n"
    #         f"Therefore, Model {model} is {strength} better than Model {other_model}.\n\n"
    #         "Rephrase the text for grammar and clarity only. "
    #         "Do NOT change structure or format. Do not add or remove information.\n\n"
    #         ":white_tick: Consistent structure\n:white_tick: Perfect grammar and phrasing\n:white_tick: Human-sounding clarity\n:white_tick: Zero format drift"
    #     )
    # else:  # Outcome Performance
        template = (
            f"Model {model} is preferred based on outcome performance.\n"
            f"In terms of key results, {key_req}.\n"
            f"Regarding supplementary information, {supp_info}.\n"
            f"Additionally, {extra}.\n"
            f"Therefore, Model {model} is {strength} better than Model {other_model}.\n\n"
            "Rephrase the text for grammar and clarity only. "
            "Do NOT change structure or format. Do not add or remove information.\n\n"
            ":white_tick: Consistent structure\n:white_tick: Perfect grammar and phrasing\n:white_tick: Human-sounding clarity\n:white_tick: Zero format drift"
        )



    # Determine model names and strength from preference
    preference_map = {
        "Model A Strongly": ("A", "B", "strongly"),
        "Model A Slightly": ("A", "B", "slightly"),
        "Neutral": ("A", "B", "neutral"),
        "Model B Slightly": ("B", "A", "slightly"),
        "Model B Strongly": ("B", "A", "strongly"),
        "Unsure": ("A", "B", "unsure"),
    }
    model, other_model, strength = preference_map.get(preference, ("A", "B", "neutral"))

    # ✳️ Handle Neutral and Unsure separately (no comparison statements)
    if strength == "neutral":
        template = (
            f"Both models performed equally well on the task.\n"
            f"In terms of key requirements, {key_req or 'both satisfied the necessary conditions'}.\n"
            f"In terms of supplementary information, {supp_info or 'both provided comparable additional details'}.\n"
            f"{f'Additional notes: {extra}.' if extra else ''}\n"
            f"Therefore, there is no clear preference between Model A and Model B.\n\n"
            "Polish this text for grammar and clarity only. Keep it neutral and factual.\n\n"
            "✅ Balanced tone\n✅ Neutral phrasing\n✅ Human-sounding clarity\n✅ Zero format drift"
        )

    elif strength == "unsure":
        template = (
            f"The available information is insufficient to determine a clear preference.\n"
            f"In terms of key requirements, {key_req or 'details were limited or inconclusive'}.\n"
            f"In terms of supplementary information, {supp_info or 'no major differences were observed'}.\n"
            f"{f'Additional notes: {extra}.' if extra else ''}\n"
            f"Therefore, the preference is marked as Unsure.\n\n"
            "Polish this text for grammar and clarity only. Keep it neutral and uncertain without implying preference.\n\n"
            "✅ Balanced tone\n✅ No implied bias\n✅ Human-sounding clarity\n✅ Zero format drift"
        )

    # ✅ Normal comparison cases
    elif type_ == "Process Performance":
        extra_line = f"Considering efficiency and errors, {extra}.\n" if extra else ""
        template = (
            f"Model {model} is preferred based on process performance.\n"
            f"In terms of key requirements, {key_req}.\n"
            f"In terms of supplementary information, {supp_info}.\n"
            f"{extra_line}"
            f"Therefore, Model {model} is {strength} better than Model {other_model}.\n\n"
            "Rephrase the text for grammar and clarity only. "
            "Do NOT change structure or format. Do not add or remove information.\n\n"
            "✅ Consistent structure\n✅ Perfect grammar and phrasing\n✅ Human-sounding clarity\n✅ Zero format drift"
        )

    else:  # Outcome Performance
        extra_line = f"Additionally, {extra}.\n" if extra else ""
        template = (
            f"Model {model} is preferred based on outcome performance.\n"
            f"In terms of key results, {key_req}.\n"
            f"In terms of supplementary information, {supp_info}.\n"
            f"{extra_line}"
            f"Therefore, Model {model} is {strength} better than Model {other_model}.\n\n"
            "Rephrase the text for grammar and clarity only. "
            "Do NOT change structure or format. Do not add or remove information.\n\n"
            "✅ Consistent structure\n✅ Perfect grammar and phrasing\n✅ Human-sounding clarity\n✅ Zero format drift"
        )



    # Send to Gemini for polishing
    try:
        if client is None:
            return {"formatted": template}
            
        response = client.models.generate_content(
            model="gemini-2.0-flash-exp",
            contents=f"You are a professional writing assistant. Polish the following text:\n\n{template}"
        )
        print("Gemini response:", response)

        polished = (response.text or "").strip()
        if not polished:
            return {"formatted": template}

        return {"formatted": polished}

    except Exception as e:
        print("Gemini API error:", e)
        return {"formatted": template}
