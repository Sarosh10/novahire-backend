from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from ai_engine import AIEngine

app = FastAPI()

# AI ENGINE OBJECT

engine = AIEngine()

# CORS

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# TEST ROUTE

@app.get("/test")
def test():
    return {"message": "Backend Running"}

# LOGIN ROUTE

@app.post("/login")
def login(data: dict):

    return {
        "message": "Login Success",
        "user": data
    }

# REGISTER ROUTE

@app.post("/register")
def register(data: dict):

    return {
        "message": "Register Success",
        "user": data
    }

# SIGNUP ROUTE

@app.post("/signup")
def signup(data: dict):

    return {
        "message": "Signup Success",
        "user": data
    }

# AI EVALUATION ROUTE

@app.post("/evaluate")
def evaluate(data: dict):

    result = engine.evaluate_answer(

        data["answer"],

        data["keywords"],

        data["ideal_answer"]
    )

    return result