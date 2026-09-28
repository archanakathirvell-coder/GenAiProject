import os
import json
import re
from typing import Dict, Any

from dotenv import load_dotenv
from google import genai
from google.genai import types

load_dotenv()

API_KEY = os.getenv("GEMINI_API_KEY")
MODEL = os.getenv("GEMINI_MODEL", "gemini-1.5-flash")

client = genai.Client(api_key=API_KEY) if API_KEY else None

def build_prompt(data: Dict[str, Any]) -> str:
    planner = data["planner"]

    if planner == "Home Interior":
        return f"""
You are PocketSmart AI, a budget-aware home interior recommendation assistant.

User budget: ₹{data['budget']}
Rooms: {data['rooms']}
Requirements: {data['requirements']}
Style: {data['style']}

Create a practical plan that stays within the total budget.
Give category-wise allocation and 3-5 example product/service suggestions.
Mention that actual prices and availability must be verified on the platform.

Return JSON with:
{{
  "budget": number,
  "allocation": [{{"category": string, "amount": number}}],
  "recommendations": [
    {{"item": string, "estimated_price": number, "platform": string, "reason": string}}
  ],
  "tips": [string]
}}
"""

    if planner == "Party":
        return f"""
You are PocketSmart AI, a budget-aware party planner.

Total budget: ₹{data['budget']}
Guests: {data['guests']}
Event type: {data['event_type']}
Venue preference: {data['venue']}
Location: {data['location']}

Allocate the budget across food/catering, venue, decoration and entertainment.
Give practical example options. Do not claim live prices or availability.

Return JSON with:
{{
  "budget": number,
  "allocation": [{{"category": string, "amount": number}}],
  "recommendations": [
    {{"category": string, "option": string, "estimated_price": number, "platform": string, "reason": string}}
  ],
  "tips": [string]
}}
"""

    if planner == "Jewelry":
        return f"""
You are PocketSmart AI, a jewelry recommendation assistant.

Budget: ₹{data['budget']}
Occasion: {data['occasion']}
Preferred style: {data['style']}
Outfit description: {data['outfit_description']}

Suggest jewelry that fits the occasion, style and budget.
If an outfit image is supplied separately, use it only for broad color/style coordination.
Do not identify a person in the image.

Return JSON with:
{{
  "budget": number,
  "recommendations": [
    {{"item": string, "estimated_price": number, "platform": string, "reason": string}}
  ],
  "styling_tips": [string]
}}
"""

    raise ValueError("Unknown planner")

async def generate_recommendation(data: Dict[str, Any]):
    if not client:
        return fallback_recommendation(data)

    prompt = build_prompt(data)
    parts = [types.Part.from_text(text=prompt)]

    if data.get("image_base64"):
        import base64
        image_bytes = base64.b64decode(data["image_base64"])
        parts.append(types.Part.from_bytes(
            data=image_bytes,
            mime_type="image/jpeg"
        ))

    try:
        response = client.models.generate_content(
            model=MODEL,
            contents=parts,
            config=types.GenerateContentConfig(
                temperature=0.4,
                response_mime_type="application/json"
            )
        )
        text = response.text.strip()
        return json.loads(text)
    except Exception as exc:
        print("Gemini error:", exc)
        return fallback_recommendation(data)

def fallback_recommendation(data: Dict[str, Any]):
    budget = float(data["budget"])

    if data["planner"] == "Home Interior":
        return {
            "budget": budget,
            "allocation": [
                {"category": "Furniture", "amount": round(budget * .40, 2)},
                {"category": "Lighting", "amount": round(budget * .15, 2)},
                {"category": "Decor", "amount": round(budget * .20, 2)},
                {"category": "Storage", "amount": round(budget * .15, 2)},
                {"category": "Contingency", "amount": round(budget * .10, 2)}
            ],
            "recommendations": [
                {"item": "Budget furniture", "estimated_price": round(budget*.40,2), "platform": "Amazon/IKEA", "reason": "Fits the furniture allocation"},
                {"item": "LED lighting", "estimated_price": round(budget*.15,2), "platform": "Amazon", "reason": "Practical and energy efficient"},
                {"item": "Decor accessories", "estimated_price": round(budget*.20,2), "platform": "Amazon/IKEA", "reason": "Adds style within budget"}
            ],
            "tips": ["Compare current prices before buying."]
        }

    if data["planner"] == "Party":
        return {
            "budget": budget,
            "allocation": [
                {"category": "Food", "amount": round(budget*.45,2)},
                {"category": "Venue", "amount": round(budget*.25,2)},
                {"category": "Decoration", "amount": round(budget*.15,2)},
                {"category": "Entertainment", "amount": round(budget*.10,2)},
                {"category": "Contingency", "amount": round(budget*.05,2)}
            ],
            "recommendations": [
                {"category": "Food", "option": "Catering package", "estimated_price": round(budget*.45,2), "platform": "Swiggy/Zomato", "reason": "Convenient for group orders"},
                {"category": "Venue", "option": "Local event venue", "estimated_price": round(budget*.25,2), "platform": "Local vendors", "reason": "Keep venue cost controlled"},
                {"category": "Decoration", "option": "Theme decoration", "estimated_price": round(budget*.15,2), "platform": "Local vendors", "reason": "Supports event theme"}
            ],
            "tips": ["Confirm venue, food quantity and final prices directly with vendors."]
        }

    return {
        "budget": budget,
        "recommendations": [
            {"item": "Stud earrings", "estimated_price": round(budget*.25,2), "platform": "Amazon/Flipkart", "reason": "Simple and versatile"},
            {"item": "Necklace set", "estimated_price": round(budget*.45,2), "platform": "Amazon/Flipkart", "reason": "Suitable for special occasions"},
            {"item": "Bracelet/bangles", "estimated_price": round(budget*.20,2), "platform": "Amazon/Flipkart", "reason": "Complements the look"}
        ],
        "styling_tips": ["Match metal tone and overall style with the outfit."]
    }
