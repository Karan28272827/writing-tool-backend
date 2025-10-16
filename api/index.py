# from fastapi import FastAPI, HTTPException, Request
# from fastapi.middleware.cors import CORSMiddleware
# from fastapi.responses import JSONResponse
# from pydantic import BaseModel
# from google import genai
# import os
# import re
# from dotenv import load_dotenv
# from openai import OpenAI

# # Load environment variables
# load_dotenv()

# app = FastAPI()

# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=["https://writing-tool-frontend.vercel.app","http://localhost:3000"],
#     allow_credentials=True,
#     allow_origin_regex=r"https://.*\.vercel\.app",
#     allow_methods=["*"],
#     allow_headers=["*"],
#     expose_headers=["*"],
# )

# # Initialize Gemini client
# API_KEY = os.getenv("GOOGLE_API_KEY")
# if not API_KEY:
#     print("Warning: GOOGLE_API_KEY not set in environment")
#     client = None
# else:
#     client = genai.Client(api_key=API_KEY)


# @app.get("/")
# def root():
#     return {"message": "✅ FastAPI Writing Tool Backend running"}


# @app.options("/{path:path}")
# async def options_handler(request: Request, path: str):
#     return JSONResponse(content={"message": "OK"})


# class FormatRequest(BaseModel):
#     type: str
#     preference: str
#     key_req: str
#     supp_info: str
#     extra: str


# @app.post("/format")
# async def format_text(request: FormatRequest):
#     type_ = request.type.strip()
#     preference = request.preference.strip()
#     key_req = request.key_req.strip()
#     supp_info = request.supp_info.strip()
#     extra = request.extra.strip()

#     if not (key_req or supp_info or extra):
#         raise HTTPException(status_code=400, detail="Empty text")

#     if len(key_req + supp_info + extra) > 2000:
#         raise HTTPException(
#             status_code=400, detail="Input too long (max 2000 chars)")

#     # Determine model names and strength from preference
#     # preference_map = {
#     #     "Model A Strongly": ("A", "B", "strongly"),
#     #     "Model A Slightly": ("A", "B", "slightly"),
#     #     "Neutral": ("A", "B", "neutral"),
#     #     "Model B Slightly": ("B", "A", "slightly"),
#     #     "Model B Strongly": ("B", "A", "strongly"),
#     #     "Unsure": ("A", "B", "unsure"),
#     # }
#     # model, other_model, strength = preference_map.get(
#     #     preference, ("A", "B", "neutral"))

#     # # Select template based on type
#     # if type_ == "Process Performance":
#     #     template = (
#     #         f"Model {model} is preferred based on process performance.\n"
#     #         f"In terms of key requirements, {key_req}.\n"
#     #         f"Regarding supplementary information, {supp_info}.\n"
#     #         f"Considering efficiency and errors, {extra}.\n"
#     #         f"Therefore, Model {model} is {strength} better than Model {other_model}.\n\n"
#     #         "Rephrase the text for grammar and clarity only. "
#     #         "Do NOT change structure or format. Do not add or remove information.\n\n"
#     #         ":white_tick: Consistent structure\n:white_tick: Perfect grammar and phrasing\n:white_tick: Human-sounding clarity\n:white_tick: Zero format drift"
#     #     )
#     # else:  # Outcome Performance
#         template = (
#             f"Model {model} is preferred based on outcome performance.\n"
#             f"In terms of key results, {key_req}.\n"
#             f"Regarding supplementary information, {supp_info}.\n"
#             f"Additionally, {extra}.\n"
#             f"Therefore, Model {model} is {strength} better than Model {other_model}.\n\n"
#             "Rephrase the text for grammar and clarity only. "
#             "Do NOT change structure or format. Do not add or remove information.\n\n"
#             ":white_tick: Consistent structure\n:white_tick: Perfect grammar and phrasing\n:white_tick: Human-sounding clarity\n:white_tick: Zero format drift"
#         )



#     # Determine model names and strength from preference
#     preference_map = {
#         "Model A Strongly": ("A", "B", "strongly"),
#         "Model A Slightly": ("A", "B", "slightly"),
#         "Neutral": ("A", "B", "neutral"),
#         "Model B Slightly": ("B", "A", "slightly"),
#         "Model B Strongly": ("B", "A", "strongly"),
#         "Unsure": ("A", "B", "unsure"),
#     }
#     model, other_model, strength = preference_map.get(preference, ("A", "B", "neutral"))

#     # ✳️ Handle Neutral and Unsure separately (no comparison statements)
#     if strength == "neutral":
#         template = (
#             f"Both models performed equally well on the task.\n"
#             f"In terms of key requirements, {key_req or 'both satisfied the necessary conditions'}.\n"
#             f"In terms of supplementary information, {supp_info or 'both provided comparable additional details'}.\n"
#             f"{f'Additional notes: {extra}.' if extra else ''}\n"
#             f"Therefore, there is no clear preference between Model A and Model B.\n\n"
#             "Polish this text for grammar and clarity only. Keep it neutral and factual.\n\n"
#             "✅ Balanced tone\n✅ Neutral phrasing\n✅ Human-sounding clarity\n✅ Zero format drift"
#         )

#     elif strength == "unsure":
#         template = (
#             f"The available information is insufficient to determine a clear preference.\n"
#             f"In terms of key requirements, {key_req or 'details were limited or inconclusive'}.\n"
#             f"In terms of supplementary information, {supp_info or 'no major differences were observed'}.\n"
#             f"{f'Additional notes: {extra}.' if extra else ''}\n"
#             f"Therefore, the preference is marked as Unsure.\n\n"
#             "Polish this text for grammar and clarity only. Keep it neutral and uncertain without implying preference.\n\n"
#             "✅ Balanced tone\n✅ No implied bias\n✅ Human-sounding clarity\n✅ Zero format drift"
#         )

#     # ✅ Normal comparison cases
#     elif type_ == "Process Performance":
#         extra_line = f"Considering efficiency and errors, {extra}.\n" if extra else ""
#         template = (
#             f"In terms of key requirements, {key_req}.\n"
#             f"In terms of supplementary information, {supp_info}.\n"
#             f"{extra_line}"
#             f"Therefore, Model {model} is {strength} better than Model {other_model}.\n\n"
#             "Rephrase the text for grammar and clarity only. "
#             "Do NOT change structure or format. Do not add or remove information.\n\n"
#             "✅ Consistent structure\n✅ Perfect grammar and phrasing\n✅ Human-sounding clarity\n✅ Zero format drift"
#         )

#     else:  # Outcome Performance
#         extra_line = f"Additionally, {extra}.\n" if extra else ""
#         template = (
#             f"In terms of key results, {key_req}.\n"
#             f"In terms of supplementary information, {supp_info}.\n"
#             f"{extra_line}"
#             f"Therefore, Model {model} is {strength} better than Model {other_model}.\n\n"
#             "Rephrase the text for grammar and clarity only. "
#             "Do NOT change structure or format. Do not add or remove information.\n\n"
#             "✅ Consistent structure\n✅ Perfect grammar and phrasing\n✅ Human-sounding clarity\n✅ Zero format drift"
#         )



#     # Send to Gemini for polishing
#     try:
#         if client is None:
#             return {"formatted": template}
            
#         response = client.models.generate_content(
#             model="gemini-2.0-flash-exp",
#             contents=f"You are a professional writing assistant. Polish the following text:\n\n{template}"
#         )
#         print("Gemini response:", response)

#         polished = (response.text or "").strip()
#         if not polished:
#             return {"formatted": template}

#         return {"formatted": polished}

#     except Exception as e:
#         print("Gemini API error:", e)
#         return {"formatted": template}


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

    # --- Template Construction ---
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
            f"The evaluation could not be completed due to certain issues or limitations.\n"
            f"{extra if extra else 'No further details were provided by the annotator.'}\n"
            f"Therefore, the preference is marked as Unsure, as a valid comparison between the models could not be established.\n\n"
            "Polish this text for grammar and clarity only. Keep it factual, formal, and concise without implying comparison.\n\n"
            ":white_tick: Proper formatting\n:white_tick: Neutral tone\n:white_tick: Human-sounding clarity\n:white_tick: Clear closing statement"
        )


    elif type_ == "Process Performance":
        extra_line = f"Considering efficiency and errors, {extra}.\n" if extra else ""
        template = (
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
            f"In terms of key results, {key_req}.\n"
            f"In terms of supplementary information, {supp_info}.\n"
            f"{extra_line}"
            f"Therefore, Model {model} is {strength} better than Model {other_model}.\n\n"
            "Rephrase the text for grammar and clarity only. "
            "Do NOT change structure or format. Do not add or remove information.\n\n"
            "✅ Consistent structure\n✅ Perfect grammar and phrasing\n✅ Human-sounding clarity\n✅ Zero format drift"
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
