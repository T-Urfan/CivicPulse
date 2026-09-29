"""Idempotent database seeder for CivicPulse.

Loads at least 30 realistic Urdu-influenced English complaints into the
database. Idempotent: running it twice will not duplicate rows or
change existing seeded rows.
"""

import asyncio
import logging
from pathlib import Path
import sys
from typing import Any

# Ensure project root is in sys.path when running directly as a script
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import AsyncSessionLocal
from app.repositories.models import DBComplaint

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

SEED_DATA: list[dict[str, Any]] = [
    {
        "text": "water line is broken near chungi no 3, please fix it is wasting water",
        "location": "Chungi No 3, Multan",
        "category": "water",
        "priority": "high",
        "status": "open",
        "ai_summary": "Broken water line at Chungi No 3",
        "triaged_by": "llm:groq"
    },
    {
        "text": "light is not coming since morning in our area",
        "location": "Gulshan-e-Iqbal, Karachi",
        "category": "electricity",
        "priority": "high",
        "status": "open",
        "ai_summary": "Power outage since morning",
        "triaged_by": "llm:groq"
    },
    {
        "text": "kachra everywhere outside my street, municipal committee not cleaning",
        "location": "Street 4, Satellite Town, Rawalpindi",
        "category": "sanitation",
        "priority": "normal",
        "status": "open",
        "ai_summary": "Garbage accumulation in street",
        "triaged_by": "llm:groq"
    },
    {
        "text": "road is fully broken and cars are getting damaged daily",
        "location": "University Road, Peshawar",
        "category": "roads",
        "priority": "high",
        "status": "in_progress",
        "ai_summary": "Severe road damage causing vehicle issues",
        "triaged_by": "llm:ollama"
    },
    {
        "text": "street lights are off for one week, very dark and unsafe at night",
        "location": "DHA Phase 2, Lahore",
        "category": "streetlights",
        "priority": "normal",
        "status": "open",
        "ai_summary": "Streetlights not working for a week",
        "triaged_by": "rules:fallback"
    },
    {
        "text": "transformer blasted with loud noise, wire is hanging on street",
        "location": "Block M, North Nazimabad, Karachi",
        "category": "electricity",
        "priority": "high",
        "status": "open",
        "ai_summary": "Transformer exploded, live wire hazard",
        "triaged_by": "llm:groq"
    },
    {
        "text": "sewerage water is entering our houses, please send gutter machine",
        "location": "Shahdara, Lahore",
        "category": "sanitation",
        "priority": "high",
        "status": "open",
        "ai_summary": "Sewage overflow entering homes",
        "triaged_by": "llm:groq"
    },
    {
        "text": "need speed breakers on this road, bikes go very fast",
        "location": "F-8 Markaz, Islamabad",
        "category": "roads",
        "priority": "low",
        "status": "open",
        "ai_summary": "Request for speed breakers due to fast driving",
        "triaged_by": "llm:groq"
    },
    {
        "text": "WASA did not supply water today in our sector",
        "location": "Sector G-10, Islamabad",
        "category": "water",
        "priority": "normal",
        "status": "open",
        "ai_summary": "No water supply today",
        "triaged_by": "llm:groq"
    },
    {
        "text": "nobody picking up garbage from the main bin for 3 days, smell is too much",
        "location": "Clifton Block 5, Karachi",
        "category": "sanitation",
        "priority": "normal",
        "status": "in_progress",
        "ai_summary": "Garbage bin unemptied for 3 days",
        "triaged_by": "llm:groq"
    },
    {
        "text": "manhole cover is missing on main road, kid can fall",
        "location": "Main Boulevard, Gulberg, Lahore",
        "category": "roads",
        "priority": "high",
        "status": "open",
        "ai_summary": "Missing manhole cover on main road",
        "triaged_by": "llm:ollama"
    },
    {
        "text": "voltage is fluctuating too much, AC and fridge will burn",
        "location": "Model Town, Gujranwala",
        "category": "electricity",
        "priority": "high",
        "status": "open",
        "ai_summary": "Severe voltage fluctuation risk to appliances",
        "triaged_by": "llm:groq"
    },
    {
        "text": "stray dogs are biting kids in the evening, please take action",
        "location": "Johar Town, Lahore",
        "category": "other",
        "priority": "high",
        "status": "open",
        "ai_summary": "Stray dog attacks in the area",
        "triaged_by": "llm:groq"
    },
    {
        "text": "the single streetlight pole in front of mosque is sparking",
        "location": "Qasimabad, Hyderabad",
        "category": "streetlights",
        "priority": "high",
        "status": "open",
        "ai_summary": "Sparking streetlight near mosque",
        "triaged_by": "rules:fallback"
    },
    {
        "text": "water tastes like sewage line mixed in it",
        "location": "Saddar, Rawalpindi",
        "category": "water",
        "priority": "high",
        "status": "open",
        "ai_summary": "Drinking water contaminated with sewage",
        "triaged_by": "llm:groq"
    },
    {
        "text": "lots of potholes in the street after recent rain",
        "location": "Township, Lahore",
        "category": "roads",
        "priority": "normal",
        "status": "resolved",
        "ai_summary": "Potholes developed after rain",
        "triaged_by": "llm:groq"
    },
    {
        "text": "sweeper is demanding extra money to pick up regular trash",
        "location": "Bahria Town Phase 7, Rawalpindi",
        "category": "sanitation",
        "priority": "low",
        "status": "open",
        "ai_summary": "Sweeper asking for unauthorized fees",
        "triaged_by": "llm:ollama"
    },
    {
        "text": "tree fell on the electricity wires due to storm",
        "location": "Cantonment, Peshawar",
        "category": "electricity",
        "priority": "high",
        "status": "in_progress",
        "ai_summary": "Fallen tree pulled down power lines",
        "triaged_by": "llm:groq"
    },
    {
        "text": "water tanker price is too high and line water is zero",
        "location": "Orangi Town, Karachi",
        "category": "water",
        "priority": "high",
        "status": "open",
        "ai_summary": "No line water, tankers overpriced",
        "triaged_by": "llm:groq"
    },
    {
        "text": "street lights turn on during the day and off at night",
        "location": "Latifabad, Hyderabad",
        "category": "streetlights",
        "priority": "low",
        "status": "open",
        "ai_summary": "Streetlight timer malfunction",
        "triaged_by": "rules:fallback"
    },
    {
        "text": "illegal parking structure built on the footpath",
        "location": "Liberty Market, Lahore",
        "category": "other",
        "priority": "normal",
        "status": "open",
        "ai_summary": "Illegal structure blocking footpath",
        "triaged_by": "llm:groq"
    },
    {
        "text": "drain is totally blocked outside shop number 12",
        "location": "Anarkali Bazaar, Lahore",
        "category": "sanitation",
        "priority": "normal",
        "status": "open",
        "ai_summary": "Blocked drain outside shop",
        "triaged_by": "llm:ollama"
    },
    {
        "text": "meter reader didn't come but we got a fake reading bill",
        "location": "G-9 Markaz, Islamabad",
        "category": "electricity",
        "priority": "normal",
        "status": "resolved",
        "ai_summary": "Incorrect electricity bill reading",
        "triaged_by": "llm:groq"
    },
    {
        "text": "main pipe leaked, whole street is like a river now",
        "location": "Wapda Town, Multan",
        "category": "water",
        "priority": "high",
        "status": "open",
        "ai_summary": "Major pipe leak flooding street",
        "triaged_by": "llm:groq"
    },
    {
        "text": "road divider is broken, cars coming wrong way",
        "location": "Ferozepur Road, Lahore",
        "category": "roads",
        "priority": "high",
        "status": "open",
        "ai_summary": "Broken road divider causing wrong-way traffic",
        "triaged_by": "llm:groq"
    },
    {
        "text": "dead animal on the corner plot giving very bad smell",
        "location": "DHA Phase 5, Karachi",
        "category": "sanitation",
        "priority": "high",
        "status": "open",
        "ai_summary": "Dead animal causing odor on corner plot",
        "triaged_by": "llm:groq"
    },
    {
        "text": "no electricity for 10 hours, UPS also dead now",
        "location": "Lyari, Karachi",
        "category": "electricity",
        "priority": "high",
        "status": "in_progress",
        "ai_summary": "Extended power outage over 10 hours",
        "triaged_by": "llm:ollama"
    },
    {
        "text": "we requested new water connection 3 months ago, nothing yet",
        "location": "I-8/4, Islamabad",
        "category": "water",
        "priority": "normal",
        "status": "open",
        "ai_summary": "Delayed new water connection request",
        "triaged_by": "llm:groq"
    },
    {
        "text": "contractor left the road dug up and didn't put asphalt",
        "location": "Bosan Road, Multan",
        "category": "roads",
        "priority": "high",
        "status": "open",
        "ai_summary": "Unfinished road construction left hazard",
        "triaged_by": "rules:fallback"
    },
    {
        "text": "half of the streetlights in this block are broken",
        "location": "Gulshan-e-Ravi, Lahore",
        "category": "streetlights",
        "priority": "normal",
        "status": "open",
        "ai_summary": "Multiple broken streetlights in block",
        "triaged_by": "llm:groq"
    }
]

async def seed_db(session: AsyncSession) -> None:
    """Check if table is empty, if so, seed exactly 30 realistic complaints."""
    # Check for existing data
    result = await session.execute(select(func.count()).select_from(DBComplaint))
    count = result.scalar_one()

    if count > 0:
        logger.info(f"Database already contains {count} complaints. Idempotent seed skipped.")
        return

    logger.info(f"Seeding {len(SEED_DATA)} complaints...")
    for item in SEED_DATA:
        db_item = DBComplaint(**item)
        session.add(db_item)
        
    await session.commit()
    logger.info("Seeding complete.")

async def main() -> None:
    async with AsyncSessionLocal() as session:
        await seed_db(session)

if __name__ == "__main__":
    asyncio.run(main())
