# backend/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from query import ask

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_methods=["POST"],
    allow_headers=["*"],
)

class Turn(BaseModel):
    user: str
    rabbi: str

class QuestionRequest(BaseModel):
    question: str
    history: list[Turn] = []

@app.post("/ask")
async def ask_rabbi(req: QuestionRequest):
    history = [{"user": t.user, "rabbi": t.rabbi} for t in req.history]
    result = ask(req.question, history)
    return result