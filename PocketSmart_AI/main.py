import os, json, base64
from pathlib import Path
from typing import Optional

from fastapi import FastAPI, Request, Form, UploadFile, File, Depends, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from starlette.middleware.sessions import SessionMiddleware
from passlib.context import CryptContext
from dotenv import load_dotenv

from gemini_utils import generate_recommendation

load_dotenv()

app = FastAPI(title="PocketSmart AI", version="1.0.0")
app.add_middleware(
    SessionMiddleware,
    secret_key=os.getenv("SESSION_SECRET", "change-this-secret")
)

BASE_DIR = Path(__file__).resolve().parent
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))
app.mount("/static", StaticFiles(directory=str(BASE_DIR / "static")), name="static")

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
USERS = {}          # Demo only. Replace with SQLite/PostgreSQL in production.
HISTORY = {}        # Demo only.

def current_user(request: Request):
    username = request.session.get("username")
    return username

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("index.html", {
        "request": request,
        "user": current_user(request)
    })

@app.get("/register", response_class=HTMLResponse)
async def register_page(request: Request):
    return templates.TemplateResponse("register.html", {"request": request})

@app.post("/register")
async def register(username: str = Form(...), password: str = Form(...)):
    if username in USERS:
        raise HTTPException(400, "Username already exists")
    USERS[username] = pwd_context.hash(password)
    HISTORY[username] = []
    return RedirectResponse("/login", status_code=303)

@app.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

@app.post("/login")
async def login(request: Request, username: str = Form(...), password: str = Form(...)):
    if username not in USERS or not pwd_context.verify(password, USERS[username]):
        raise HTTPException(401, "Invalid username or password")
    request.session["username"] = username
    return RedirectResponse("/dashboard", status_code=303)

@app.get("/logout")
async def logout(request: Request):
    request.session.clear()
    return RedirectResponse("/", status_code=303)

@app.get("/dashboard", response_class=HTMLResponse)
async def dashboard(request: Request):
    user = current_user(request)
    if not user:
        return RedirectResponse("/login", status_code=303)
    return templates.TemplateResponse("dashboard.html", {
        "request": request,
        "user": user,
        "history": HISTORY.get(user, [])
    })

@app.get("/home-planner", response_class=HTMLResponse)
async def home_planner(request: Request):
    return templates.TemplateResponse("home_planner.html", {"request": request})

@app.get("/party-planner", response_class=HTMLResponse)
async def party_planner(request: Request):
    return templates.TemplateResponse("party_planner.html", {"request": request})

@app.get("/jewelry-planner", response_class=HTMLResponse)
async def jewelry_planner(request: Request):
    return templates.TemplateResponse("jewelry_planner.html", {"request": request})

@app.post("/generate-home")
async def generate_home(
    request: Request,
    budget: float = Form(...),
    rooms: str = Form(...),
    requirements: str = Form(...),
    style: str = Form(...)
):
    prompt_data = {
        "planner": "Home Interior",
        "budget": budget,
        "rooms": rooms,
        "requirements": requirements,
        "style": style
    }
    result = await generate_recommendation(prompt_data)

    user = current_user(request)
    if user:
        HISTORY.setdefault(user, []).append({"type": "Home", "input": prompt_data, "result": result})

    return JSONResponse({"success": True, "result": result})

@app.post("/generate-party")
async def generate_party(
    request: Request,
    budget: float = Form(...),
    guests: int = Form(...),
    event_type: str = Form(...),
    venue: str = Form(...),
    location: str = Form(...)
):
    prompt_data = {
        "planner": "Party",
        "budget": budget,
        "guests": guests,
        "event_type": event_type,
        "venue": venue,
        "location": location
    }
    result = await generate_recommendation(prompt_data)

    user = current_user(request)
    if user:
        HISTORY.setdefault(user, []).append({"type": "Party", "input": prompt_data, "result": result})

    return JSONResponse({"success": True, "result": result})

@app.post("/generate-jewelry")
async def generate_jewelry(
    request: Request,
    budget: float = Form(...),
    occasion: str = Form(...),
    style: str = Form(...),
    outfit_description: str = Form(""),
    outfit_image: Optional[UploadFile] = File(None)
):
    image_b64 = None
    if outfit_image and outfit_image.filename:
        data = await outfit_image.read()
        image_b64 = base64.b64encode(data).decode("utf-8")

    prompt_data = {
        "planner": "Jewelry",
        "budget": budget,
        "occasion": occasion,
        "style": style,
        "outfit_description": outfit_description,
        "image_base64": image_b64
    }
    result = await generate_recommendation(prompt_data)

    user = current_user(request)
    if user:
        HISTORY.setdefault(user, []).append({"type": "Jewelry", "input": {k:v for k,v in prompt_data.items() if k != "image_base64"}, "result": result})

    return JSONResponse({"success": True, "result": result})

@app.get("/session-info")
async def session_info(request: Request):
    user = current_user(request)
    return {"logged_in": bool(user), "user_id": user}

@app.get("/session-data")
async def session_data(request: Request):
    user = current_user(request)
    if not user:
        raise HTTPException(401, "Not logged in")
    return {"user": user, "history": HISTORY.get(user, [])}

@app.get("/history")
async def history(request: Request):
    user = current_user(request)
    if not user:
        raise HTTPException(401, "Not logged in")
    return {"history": HISTORY.get(user, [])}

@app.get("/recommendations-details")
async def recommendation_details(request: Request, category: str):
    user = current_user(request)
    if not user:
        raise HTTPException(401, "Not logged in")
    return {
        "category": category,
        "history": [x for x in HISTORY.get(user, []) if x["type"].lower() == category.lower()]
    }

@app.on_event("startup")
async def startup():
    print("PocketSmart AI started.")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
