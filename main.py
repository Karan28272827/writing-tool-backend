from fastapi import FastAPI, Form
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# Allow your frontend to call this backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Next.js dev server
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def root():
    return {"message": "FastAPI Writing Tool Backend is running 🚀"}

@app.post("/format")
def format_text(thoughts: str = Form(...)):
    # Basic text cleaning logic (can be replaced with AI later)
    formatted = (
        f"📄 Standardized Response\n\n"
        f"🧠 User Thoughts:\n{thoughts}\n\n"
        f"✅ Polished Output:\n{thoughts.strip().capitalize()}."
    )
    return {"formatted": formatted}
