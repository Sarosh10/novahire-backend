from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

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

@app.post("/register")
def login(data: dict):
    return {
        "message": "Register Success",
        "user": data
    }
@app.post("/signup")
def signup(data: dict):
    return {
        "message": "Signup Success",
        "user": data
    }

# REGISTER ROUTE

@app.post("/register")
def register(data: dict):
    return {
        "message": "Register Success",
        "user": data
    }