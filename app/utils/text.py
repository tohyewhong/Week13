
import re

SYSTEM_INTENT_HINTS = {
    "rag": ["from the document", "according to", "cite", "source"],
    "t2i": ["draw", "image", "generate a picture", "logo", "icon"],
    "weather": ["weather", "temperature", "forecast"],
    "sql": ["sql", "query", "table", "database"],
    "recommender": ["recommend", "suggest", "similar"]
}

def normalize(s: str) -> str:
    return re.sub(r"\s+", " ", s.strip())

def detect_intent(user_text: str) -> str:
    t = user_text.lower()
    
    # Check for SQL queries first (most specific)
    if t.startswith("select") or "select" in t:
        return "sql"
    
    # Check other intents
    for intent, keys in SYSTEM_INTENT_HINTS.items():
        if any(k in t for k in keys):
            return intent
    return "chat"
