from datetime import date
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, HttpUrl


class Record(BaseModel):
    model_config = ConfigDict(
        extra="forbid",
        str_strip_whitespace=True,
    )


class Source(Record):
    url: HttpUrl
    title: str = Field(min_length=1)
    kind: Literal["study", "market_report", "campaign", "guidance"]
    collected_on: date
    published_on: date | None = None
    doi: str | None = None


class Evidence(Record):
    source: Source
    finding: str = Field(min_length=1)
    locator: str = Field(min_length=1)
    limitation: str = Field(min_length=1)
    markets: list[str] = Field(default_factory=list)
    audience: str = ""
    category: str = ""
    channel: str = ""
    topics: list[str] = Field(default_factory=list)


class SearchContext(Record):
    questions: list[str] = Field(min_length=1)
    market: str = Field(min_length=1)
    brand_context: str = ""
    limit: int = Field(default=5, ge=1, le=50)