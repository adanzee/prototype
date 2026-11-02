"""Precomputed fixtures for testing without an API key."""

from campaign_ai.schema.requirement import Extraction


SAMPLES = {
    "Sample 1 — missing region": (
        "Promote the Luma reusable bottle. "
        "Objective: increase online sales. "
        "Audience: university students. "
        "Channels: IG and TikTok. "
        "Tone: friendly. "
        "KPI: 500 purchases. "
        "Budget: USD 5,000. "
        "Timeline: November 2026."
    ),

    "Sample 2 — complete": (
        "Promote the Luma reusable bottle. "
        "Objective: increase online sales. "
        "Audience: university students. "
        "Region: UAE. "
        "Channels: IG and TikTok. "
        "Tone: friendly. "
        "KPI: 500 purchases. "
        "Budget: USD 5,000. "
        "Timeline: November 2026."
    ),

    "Sample 3 — contradiction": (
        "Promote the Luma reusable bottle. "
        "Objective: increase online sales. "
        "Audience: university students. "
        "Region: UAE. "
        "Channels: IG and TikTok. "
        "Use a playful tone. "
        "Use a strictly formal tone, never playful."
    ),
}


def fixture_extract(brief: str) -> Extraction:
    try:
        index = list(SAMPLES.values()).index(brief)

    except ValueError as exc:
        raise ValueError(
            "Fixture mode accepts only bundled samples. "
            "Disable DEMO_MODE for real extraction."
        ) from exc

    values = {
        "product": "Luma reusable bottle",
        "objective": "increase online sales",
        "audience": "university students",
        "channels": ["instagram", "tiktok"],
    }

    quotes = {
        "product": "Luma reusable bottle",
        "objective": "increase online sales",
        "audience": "university students",
        "channels": "IG and TikTok",
    }

    if index != 0:
        values["regions"] = ["UAE"]
        quotes["regions"] = "UAE"

    conflicts = []

    if index < 2:
        values.update(
            tone=["friendly"],
            kpis=["500 purchases"],
            budget="USD 5,000",
            timeline="November 2026",
        )

        quotes.update(
            tone="friendly",
            kpis="500 purchases",
            budget="USD 5,000",
            timeline="November 2026",
        )

    else:
        conflicts = [
            {
                "fields": ["tone"],
                "description": (
                    "Choose playful or strictly formal tone "
                    "and explain the resolution."
                ),
                "quotes": [
                    "Use a playful tone.",
                    "Use a strictly formal tone, never playful.",
                ],
            }
        ]

    return Extraction.model_validate({
        "requirements": values,
        "evidence": [
            {
                "field": field,
                "quote": quote,
            }
            for field, quote in quotes.items()
        ],
        "contradictions": conflicts,
    })