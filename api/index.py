from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from dotenv import load_dotenv
import os
import requests

# Load environment variables
load_dotenv()

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://writing-tool-frontend.vercel.app", "http://localhost:3000"],
    allow_credentials=True,
    allow_origin_regex=r"https://.*\.vercel\.app",
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
)

# Initialize DeepSeek API key
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")
if not DEEPSEEK_API_KEY:
    print("⚠️ Warning: DEEPSEEK_API_KEY not set in environment")


@app.get("/")
def root():
    return {"message": "✅ FastAPI Writing Tool Backend running with DeepSeek"}


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
        raise HTTPException(status_code=400, detail="Input too long (max 2000 chars)")

    # Determine model names and preference strength
    preference_map = {
        "Model A Strongly": ("A", "B", "strongly"),
        "Model A Slightly": ("A", "B", "slightly"),
        "Neutral": ("A", "B", "neutral"),
        "Model B Slightly": ("B", "A", "slightly"),
        "Model B Strongly": ("B", "A", "strongly"),
        "Unsure": ("A", "B", "unsure"),
    }
    model, other_model, strength = preference_map.get(preference, ("A", "B", "neutral"))

    # --- Supplementary info handling ---
    # Detect if "both" or similar terms are used, or if it's clear that both models provided info
    both_supplementary = any(
        phrase in supp_info.lower()
        for phrase in ["both", "each model", "all models", "model a and model b"]
    )

    # --- Template Construction ---
    if strength == "neutral":
        template = (
            f"Both models {key_req or 'fulfilled the key requirements successfully'}.\n"
            f"Both models {supp_info or 'provided comparable supplementary information'}.\n"
            f"{f'Both models also {extra}.' if extra else ''}\n"
            f"Therefore, there is no clear advantage between Model A and Model B.\n\n"
            "Polish this text for grammar and clarity only. Keep it neutral, factual, and concise.\n\n"
            "✅ Balanced tone\n✅ Neutral phrasing\n✅ Human-sounding clarity\n✅ Zero format drift"
        )

    elif strength == "unsure":
        template = (
            f"The comparison could not be completed due to {extra or 'unclear or missing evaluation details'}.\n"
            f"Therefore, it cannot be determined whether Model A or Model B performed better.\n\n"
            "Polish this text for grammar and clarity only. Keep it factual and formal.\n\n"
            "✅ Neutral tone\n✅ Proper formatting\n✅ Human-sounding clarity\n✅ Clear closing statement"
        )

    elif type_ == "Process Performance":
        if both_supplementary:
            supp_line = f"Both models {supp_info or 'handled supplementary information effectively'}."
        else:
            supp_line = (
                f"Model {model} {supp_info or 'completed the key steps correctly'}, "
                f"but Model {other_model} did not."
            )

        template = (
            f"Both models {key_req or 'attempted to meet the process requirements'}.\n"
            f"{supp_line}\n"
            f"{f'Model {model} made fewer errors while Model {other_model} made {extra} mistakes.' if extra else ''}\n"
            f"Therefore, Model {model} is {strength} better than Model {other_model} in process performance.\n\n"
            "Rephrase for grammar and clarity only. Do not change structure or format.\n\n"
            "✅ Consistent structure\n✅ Perfect grammar\n✅ Human-sounding clarity\n✅ Zero format drift"
        )

    else:  # Outcome Performance
        if both_supplementary:
            supp_line = f"Both models {supp_info or 'provided sufficient supplementary information, such as the company URL'}."
        else:
            supp_line = (
                f"Model {model} {supp_info or 'included additional useful results'}, "
                f"but Model {other_model} did not."
            )

        template = (
            f"In terms of key results, both models {key_req or 'produced valid and complete outputs'}.\n"
            f"{supp_line}\n"
            f"{f'Model {model} avoided {extra} mistakes that Model {other_model} made.' if extra else ''}\n"
            f"Therefore, Model {model} is {strength} better than Model {other_model} in outcome performance.\n\n"
            "Rephrase for grammar and clarity only. Do not change structure or format.\n\n"
            "✅ Consistent structure\n✅ Perfect grammar\n✅ Human-sounding clarity\n✅ Zero format drift"
        )

    # --- Send to DeepSeek API ---
    try:
        if not DEEPSEEK_API_KEY:
            return {"formatted": template}

        print("🧠 Using DeepSeek API...")
        deepseek_url = "https://api.deepseek.com/chat/completions"
        headers = {
            "Authorization": f"Bearer {DEEPSEEK_API_KEY}",
            "Content-Type": "application/json",
        }
        data = {
            "model": "deepseek-chat",
            "messages": [
                {"role": "system", "content": "You are a professional writing assistant."},
                {"role": "user", "content": f"Polish this text for grammar and clarity only:\n\n{template}"}
            ],
            "temperature": 0.4,
            "max_tokens": 500,
        }

        response = requests.post(deepseek_url, headers=headers, json=data, timeout=30)
        response.raise_for_status()
        result = response.json()

        polished = result["choices"][0]["message"]["content"].strip()
        return {"formatted": polished or template}

    except Exception as e:
        print("⚠️ DeepSeek API error:", e)
        return {"formatted": template}

