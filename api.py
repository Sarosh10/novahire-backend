from fastapi import FastAPI
from ai_voice_interview import AIInterviewAgent

app = FastAPI()

@app.get("/")
def home():
    return {"message": "AI Interview Agent API is running"}


@app.get("/start-interview")
def start():
    bot = AIInterviewAgent()
    bot.run()
    return {"message": "Interview finished"}