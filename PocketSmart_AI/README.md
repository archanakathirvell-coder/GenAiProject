# PocketSmart AI

A FastAPI + Gemini budget recommendation assistant based on the supplied project document.

## Features

- Home Interior Budget Planner
- Party Budget Planner
- Jewelry Budget Planner with optional outfit image
- Gemini-powered recommendations
- Login/register/session demo
- Recommendation history
- HTML/CSS/JavaScript frontend
- Fallback recommendations if Gemini is unavailable

## Project structure

```text
PocketSmart_AI/
├── main.py
├── gemini_utils.py
├── requirements.txt
├── .env.example
├── templates/
│   ├── base.html
│   ├── index.html
│   ├── register.html
│   ├── login.html
│   ├── dashboard.html
│   ├── home_planner.html
│   ├── party_planner.html
│   └── jewelry_planner.html
└── static/
    ├── style.css
    └── app.js
```

## Run

```bash
python -m venv venv
```

Windows:
```bash
venv\Scripts\activate
```

Linux/macOS:
```bash
source venv/bin/activate
```

Install:
```bash
pip install -r requirements.txt
```

Create `.env` from `.env.example` and add your Gemini API key.

Start:
```bash
uvicorn main:app --reload
```

Open:
http://127.0.0.1:8000

## Important

The original document mentions both Flask and FastAPI. This implementation uses FastAPI because the later milestones explicitly define FastAPI routes, Jinja2 templates and Uvicorn.

The user-data store in this starter version is in memory. For a real deployment, replace it with SQLite/PostgreSQL and use a production-grade authentication system.
