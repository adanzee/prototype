import pytest

from module_1.information_extraction.document_parser import TextBlock
from module_1.information_extraction.extractor_pipeline import ExtractorPipeline
from module_1.information_extraction.reconciliation import (
    ORDINARY_FIELDS,
    reconcile,
)
from module_1.information_extraction.requirement_schema import (
    Evidence,
    RequirementField,
    RequirementValue,
)


class FakeLLMExtractor:
    def extract(self, blocks):
        block = blocks[0]

        return {
            "brand": [{"value": "Aurelia", "confidence": 0.95}],
            "product": None,
            "product_category": None,
            "target_audience": None,
            "target_market": None,
            "positioning": None,
            "campaign_objective": None,
            "desired_qualities": None,
            "platform": None,
            "restrictions": None,
            "ambiguities": [],
            "unsupported_inference": [],
            "contradiction": [],
            "evidence": [
                {
                    "field": "brand",
                    "value": "Aurelia",
                    "text": block.text,
                    "block_id": block.block_id,
                    "source_type": block.source_type,
                    "page_number": block.page_number,
                    "section": block.section,
                }
            ],
        }


def empty_rule_result(**overrides):
    fields = {
        name: RequirementField()
        for name in ORDINARY_FIELDS
    }
    fields.update(overrides)
    return fields


def empty_extraction_result(**overrides):
    fields = {
        "brand": None,
        "product": None,
        "product_category": None,
        "target_audience": None,
        "target_market": None,
        "positioning": None,
        "campaign_objective": None,
        "desired_qualities": None,
        "platform": None,
        "restrictions": None,
        "ambiguities": [],
        "unsupported_inference": [],
        "contradiction": [],
        "evidence": [],
    }
    fields.update(overrides)
    return fields


def test_pipeline_returns_validated_requirements_and_decisions():
    block = TextBlock(
        block_id="block_1",
        text="Brand: Aurelia",
        source_type="txt",
        page_number=None,
        section=None,
    )

    pipeline = ExtractorPipeline(llm_extractor=FakeLLMExtractor())
    result = pipeline.extract([block])

    requirements = result["requirements"]
    brand = requirements.brand.value

    assert brand.value == "Aurelia"
    assert brand.confidence == 0.95
    assert result["reconciliation"]["brand"]["status"] == "accepted"

    assert any(
        evidence.extraction_method == "rule"
        for evidence in brand.evidence
    )
    assert any(
        evidence.extraction_method == "llm"
        for evidence in brand.evidence
    )


def test_pipeline_flags_conflicting_values():
    rule_evidence = Evidence(
        text="Brand: Aurelia",
        block_id="block_1",
        source_type="txt",
        extraction_method="rule",
    )

    rule_field = RequirementField(
        value=RequirementValue(
            value="Aurelia",
            evidence=[rule_evidence],
        )
    )

    llm_result = empty_extraction_result(
        brand=[{"value": "Other Brand", "confidence": 0.99}],
        evidence=[
            {
                "field": "brand",
                "value": "Other Brand",
                "text": "Other Brand",
                "block_id": "block_1",
                "source_type": "txt",
                "page_number": None,
                "section": None,
            }
        ],
    )

    decision = reconcile(
        empty_rule_result(brand=rule_field),
        llm_result,
    )["brand"]

    assert decision["status"] == "needs_resolution"
    assert decision["values"] == []


def test_pipeline_rejects_low_confidence_llm_only_value():
    llm_result = empty_extraction_result(
        brand=[{"value": "Aurelia", "confidence": 0.75}],
        evidence=[
            {
                "field": "brand",
                "value": "Aurelia",
                "text": "Brand Aurelia",
                "block_id": "block_1",
                "source_type": "txt",
                "page_number": None,
                "section": None,
            }
        ],
    )

    decision = reconcile(
        empty_rule_result(),
        llm_result,
    )["brand"]

    assert decision["status"] == "rejected"
    assert decision["values"] == []


def test_pipeline_rejects_empty_input():
    pipeline = ExtractorPipeline(llm_extractor=FakeLLMExtractor())

    with pytest.raises(
        ValueError,
        match="Cannot extract requirements from an empty brief",
    ):
        pipeline.extract([])


def test_pipeline_accepts_high_confidence_llm_only_value():
    block = TextBlock(
        block_id="block_1",
        text="The campaign is for Aurelia.",
        source_type="txt",
        page_number=None,
        section=None,
    )

    class HighConfidenceLLM:
        def extract(self, blocks):
            return empty_extraction_result(
                brand=[{"value": "Aurelia", "confidence": 0.95}],
                evidence=[{
                    "field": "brand",
                    "value": "Aurelia",
                    "text": "The campaign is for Aurelia.",
                    "block_id": "block_1",
                    "source_type": "txt",
                    "page_number": None,
                    "section": None,
                }],
            )

    result = ExtractorPipeline(llm_extractor=HighConfidenceLLM()).extract([block])

    assert result["requirements"].brand.value.value == "Aurelia"
    assert result["reconciliation"]["brand"]["status"] == "accepted"


def test_pipeline_rejects_rule_only_value():
    block = TextBlock(
        block_id="block_1",
        text="Brand: Aurelia",
        source_type="txt",
        page_number=None,
        section=None,
    )

    class EmptyLLM:
        def extract(self, blocks):
            return empty_extraction_result()

    result = ExtractorPipeline(llm_extractor=EmptyLLM()).extract([block])

    assert result["requirements"].brand.value is None
    assert result["reconciliation"]["brand"]["status"] == "rejected"


def test_pipeline_preserves_multiple_accepted_values():
    block = TextBlock(
        block_id="block_1",
        text="The campaign should run on Instagram and TikTok.",
        source_type="txt",
        page_number=None,
        section=None,
    )

    class MultiplePlatformLLM:
        def extract(self, blocks):
            return empty_extraction_result(
                platform=[
                    {"value": "Instagram", "confidence": 0.95},
                    {"value": "TikTok", "confidence": 0.96},
                ],
                evidence=[
                    {
                        "field": "platform",
                        "value": "Instagram",
                        "text": "The campaign should run on Instagram and TikTok.",
                        "block_id": "block_1",
                        "source_type": "txt",
                        "page_number": None,
                        "section": None,
                    },
                    {
                        "field": "platform",
                        "value": "TikTok",
                        "text": "The campaign should run on Instagram and TikTok.",
                        "block_id": "block_1",
                        "source_type": "txt",
                        "page_number": None,
                        "section": None,
                    },
                ],
            )

    result = ExtractorPipeline(
        llm_extractor=MultiplePlatformLLM()
    ).extract([block])

    platforms = result["requirements"].platform.value

    assert isinstance(platforms, list)
    assert {item.value for item in platforms} == {"Instagram", "TikTok"}
    assert result["reconciliation"]["platform"]["status"] == "accepted"


def test_pipeline_leaves_missing_fields_empty():
    block = TextBlock(
        block_id="block_1",
        text="A campaign brief with no explicit brand name.",
        source_type="txt",
        page_number=None,
        section=None,
    )

    class EmptyLLM:
        def extract(self, blocks):
            return empty_extraction_result()

    result = ExtractorPipeline(llm_extractor=EmptyLLM()).extract([block])

    requirements = result["requirements"]

    assert requirements.brand.value is None
    assert requirements.product.value is None
    assert result["reconciliation"]["brand"]["status"] == "unresolved"


def test_pipeline_rejects_empty_input():
    import pytest

    pipeline = ExtractorPipeline(llm_extractor=FakeLLMExtractor())

    with pytest.raises(
        ValueError,
        match="Cannot extract requirements from an empty brief",
    ):
        pipeline.extract([])
