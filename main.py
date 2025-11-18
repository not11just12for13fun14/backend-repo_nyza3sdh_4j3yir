import os
import random
from typing import Optional
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

app = FastAPI(title="Mystic Cards API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class Card(BaseModel):
    name: str
    upright_meaning: Optional[str] = None
    reversed_meaning: Optional[str] = None


# Minimal deck sample; can be expanded later
DECK: list[Card] = [
    Card(
        name="The Fool",
        upright_meaning="New beginnings, optimism, trust in life",
        reversed_meaning="Recklessness, taken advantage of, inconsideration",
    ),
    Card(
        name="The Magician",
        upright_meaning="Willpower, desire, creation, manifestation",
        reversed_meaning="Trickery, illusions, out of touch",
    ),
    Card(
        name="The High Priestess",
        upright_meaning="Intuition, unconscious, inner voice",
        reversed_meaning="Lack of center, lost inner voice, repressed feelings",
    ),
    Card(
        name="The Empress",
        upright_meaning="Motherhood, abundance, nature",
        reversed_meaning="Dependence, smothering, emptiness",
    ),
    Card(
        name="The Sun",
        upright_meaning="Joy, success, celebration, positivity",
        reversed_meaning="Negativity, depression, sadness",
    ),
]


@app.get("/")
def status_root():
    return {"status": "ok", "service": "mystic-cards-api"}


@app.get("/health")
def health():
    return {"ok": True}


@app.get("/reading/one", response_model=Card)
def pull_one():
    # Choose a random card from the deck
    card = random.choice(DECK)
    return card


@app.get("/test")
def test_database():
    """Test endpoint to check if database is available and accessible"""
    response = {
        "backend": "✅ Running",
        "database": "❌ Not Available",
        "database_url": None,
        "database_name": None,
        "connection_status": "Not Connected",
        "collections": [],
    }

    try:
        from database import db  # type: ignore

        if db is not None:
            response["database"] = "✅ Available"
            response["database_url"] = "✅ Configured"
            response["database_name"] = getattr(db, "name", "✅ Connected")
            response["connection_status"] = "Connected"
            try:
                collections = db.list_collection_names()
                response["collections"] = collections[:10]
                response["database"] = "✅ Connected & Working"
            except Exception as e:  # pragma: no cover
                response["database"] = f"⚠️  Connected but Error: {str(e)[:50]}"
        else:
            response["database"] = "⚠️  Available but not initialized"

    except ImportError:
        response["database"] = "❌ Database module not found (run enable-database first)"
    except Exception as e:  # pragma: no cover
        response["database"] = f"❌ Error: {str(e)[:50]}"

    # Check environment variables
    response["database_url"] = "✅ Set" if os.getenv("DATABASE_URL") else "❌ Not Set"
    response["database_name"] = "✅ Set" if os.getenv("DATABASE_NAME") else "❌ Not Set"

    return response


if __name__ == "__main__":
    import uvicorn

    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
