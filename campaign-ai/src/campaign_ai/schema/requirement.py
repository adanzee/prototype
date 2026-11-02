from datetime import date
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator


class StrictModel(BaseModel):
    model_config = ConfigDict(extra="forbid")


class Requirements(StrictModel):
    product: str | None = None
    objective: str | None = None
    audience: str | None = None

    regions: list[str] = Field(default_factory=list)
    channels: list[str] = Field(default_factory=list)
    excluded_channels: list[str] = Field(default_factory=list)

    tone: list[str] = Field(default_factory=list)
    kpis: list[str] = Field(default_factory=list)

    budget: str | None = None
    timeline: str | None = None

    start_date: date | None = None
    end_date: date | None = None

    deliverables: list[str] = Field(default_factory=list)
    constraints: list[str] = Field(default_factory=list)

    @field_validator(
        "product",
        "objective",
        "audience",
        "budget",
        "timeline",
        mode="before",
    )
    @classmethod
    def clean_text(cls, value):
        if value is None:
            return None

        if not isinstance(value, str):
            raise ValueError("Expected text or null")

        return value.strip() or None

    @field_validator(
        "regions",
        "channels",
        "excluded_channels",
        "tone",
        "kpis",
        "deliverables",
        "constraints",
        mode="before",
    )
    @classmethod
    def clean_list(cls, value):
        if not isinstance(value, list):
            raise ValueError("Expected a list of strings")

        if any(not isinstance(item, str) for item in value):
            raise ValueError("Expected a list of strings")

        cleaned = [
            item.strip()
            for item in value
            if item.strip()
        ]

        return list(dict.fromkeys(cleaned))

    @field_validator("channels", "excluded_channels")
    @classmethod
    def normalize_channels(cls, value):
        aliases = {
            "ig": "instagram",
            "fb": "facebook",
            "yt": "youtube",
            "tik tok": "tiktok",
        }

        normalized = [
            aliases.get(item.casefold(), item.casefold())
            for item in value
        ]

        return list(dict.fromkeys(normalized))


class Evidence(StrictModel):
    field: str
    quote: str = Field(min_length=1)

    @field_validator("field")
    @classmethod
    def known_field(cls, value):
        if value not in Requirements.model_fields:
            raise ValueError("Unknown requirement field")

        return value


class Contradiction(StrictModel):
    fields: list[str] = Field(min_length=1)
    description: str = Field(min_length=1)
    quotes: list[str] = Field(min_length=1)

    @field_validator("fields")
    @classmethod
    def known_fields(cls, values):
        if any(
            value not in Requirements.model_fields
            for value in values
        ):
            raise ValueError("Unknown contradiction field")

        return values


class Extraction(StrictModel):
    requirements: Requirements
    evidence: list[Evidence] = Field(default_factory=list)
    contradictions: list[Contradiction] = Field(default_factory=list)


class Question(StrictModel):
    id: str
    field: str
    text: str
    blocking: bool


class RequirementsResult(StrictModel):
    requirements: Requirements

    evidence: list[Evidence] = Field(default_factory=list)
    contradictions: list[Contradiction] = Field(default_factory=list)

    missing_fields: list[str] = Field(default_factory=list)
    recommended_fields: list[str] = Field(default_factory=list)

    questions: list[Question] = Field(default_factory=list)
    resolutions: dict[str, str] = Field(default_factory=dict)

    operator_edits: dict[str, object] = Field(default_factory=dict)

    status: Literal["needs_review", "approved"] = "needs_review"


class Review(StrictModel):
    edits: dict[str, object] = Field(default_factory=dict)
    resolutions: dict[str, str] = Field(default_factory=dict)
    approve: bool = False