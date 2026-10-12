
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


SCHEMA_VERSION = "1.0.0"

ExtractionMethod = Literal["rule", "ner", "llm", "hybrid"]


class Evidence(BaseModel):
    model_config = ConfigDict(extra="forbid")

    text: str = Field(min_length=1)
    block_id: str = Field(min_length=1)
    source_type: Literal["txt", "docx", "pdf", "text"]
    page_number: int | None = Field(default=None, ge=1)
    section: str | None = None
    extraction_method: ExtractionMethod



class RequirementValue(BaseModel):
    """One distinct value extracted from the campaign brief."""

    model_config = ConfigDict(extra="forbid")

    value: str = Field(min_length=1)
    confidence: float | None = Field(default=None, ge=0, le=1)
    evidence: list[Evidence] = Field(min_length=1)



class RequirementField(BaseModel):
    model_config = ConfigDict(extra="forbid")

    value: RequirementValue | list[RequirementValue] | None = None
    evidence: list[Evidence] = Field(default_factory=list)


class RequirementSchema(BaseModel):
    model_config = ConfigDict(extra="forbid")

    schema_version: Literal["1.0.0"] = SCHEMA_VERSION

    brand: RequirementField = Field(default_factory=RequirementField)
    product: RequirementField = Field(default_factory=RequirementField)
    product_category: RequirementField = Field(default_factory=RequirementField)
    target_audience: RequirementField = Field(default_factory=RequirementField)
    target_market: RequirementField = Field(default_factory=RequirementField)
    positioning: RequirementField = Field(default_factory=RequirementField)
    campaign_objective: RequirementField = Field(default_factory=RequirementField)
    desired_qualities: RequirementField = Field(default_factory=RequirementField)
    platform: RequirementField = Field(default_factory=RequirementField)
    restrictions: RequirementField = Field(default_factory=RequirementField)

    ambiguities: list[str] = Field(default_factory=list)
    unsupported_inference: list[str] = Field(default_factory=list)
    contradiction: list[str] = Field(default_factory=list)
