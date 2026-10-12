
from types import SimpleNamespace

from module_1.information_extraction.llm_extractor import LLMExtractor



class FakeGroqClient:
    def __init__(self, response: str):
        self.response = response

    def generate(self, prompt: str) -> str:
        return self.response

    
    
    





def test_extraction_and_evidence_validation():
    blocks = [
        SimpleNamespace(
            block_id="block_1",
            text="Aurelia is launching a perfume.",
            source_type="txt",
            page_number=None,
            section=None,
        )
    ]

    response = """
    {
        "brand": [{"value": "Aurelia", "confidence": 0.95}],
        "product": null,
        "product_category": null,
        "target_audience": null,
        "target_market": null,
        "positioning": null,
        "campaign_objective": null,
        "desired_qualities": null,
        "platform": null,
        "restrictions": null,
        "ambiguities": [],
        "unsupported_inference": [],
        "contradiction": [],
        "evidence": [{
            "field": "brand",
            "value": "Aurelia",
            "text": "Aurelia is launching a perfume.",
            "block_id": "block_1",
            "source_type": "txt",
            "page_number": null,
            "section": null
        }]
    }
    """

    extractor = LLMExtractor(client=FakeGroqClient(response=response))

    result = extractor.extract(blocks)

    assert result["brand"][0]["value"] == "Aurelia"
    assert result["evidence"][0]["block_id"] == "block_1"


def test_extractor_rejects_fabricated_evidence():
    blocks = [
        SimpleNamespace(
            block_id="block_1",
            text="Aurelia is launching a perfume.",
            source_type="txt",
            page_number=None,
            section=None,
        )
    ]

    response = """
    {
        "brand": [{"value": "Aurelia", "confidence": 0.95}],
        "product": null,
        "product_category": null,
        "target_audience": null,
        "target_market": null,
        "positioning": null,
        "campaign_objective": null,
        "desired_qualities": null,
        "platform": null,
        "restrictions": null,
        "ambiguities": [],
        "unsupported_inference": [],
        "contradiction": [],
        "evidence": [{
            "field": "brand",
            "value": "Aurelia",
            "text": "Aurelia is a luxury brand.",
            "block_id": "block_1",
            "source_type": "txt",
            "page_number": null,
            "section": null
        }]
    }
    """

    extractor = LLMExtractor(client=FakeGroqClient(response=response))

    import pytest

    with pytest.raises(ValueError):
        extractor.extract(blocks)



def test_extractor_rejects_invalid_confidence():
    blocks = [
        SimpleNamespace(
            block_id="block_1",
            text="Aurelia is launching a perfume.",
            source_type="txt",
            page_number=None,
            section=None,
        )
    ]

    response = """
    {
        "brand": [{"value": "Aurelia", "confidence": 1.5}],
        "product": null,
        "product_category": null,
        "target_audience": null,
        "target_market": null,
        "positioning": null,
        "campaign_objective": null,
        "desired_qualities": null,
        "platform": null,
        "restrictions": null,
        "ambiguities": [],
        "unsupported_inference": [],
        "contradiction": [],
        "evidence": [{
            "field": "brand",
            "value": "Aurelia",
            "text": "Aurelia is launching a perfume.",
            "block_id": "block_1",
            "source_type": "txt",
            "page_number": null,
            "section": null
        }]
    }
    """

    extractor = LLMExtractor(client=FakeGroqClient(response=response))

    import pytest

    with pytest.raises(ValueError):
        extractor.extract(blocks)



def test_extractor_preserves_multiple_distinct_values():
    blocks = [
        SimpleNamespace(
            block_id="block_1",
            text="The brand is Aurelia. The brand is Bellora.",
            source_type="txt",
            page_number=None,
            section=None,
        )
    ]

    response = """
    {
        "brand": [
            {"value": "Aurelia", "confidence": 0.95},
            {"value": "Bellora", "confidence": 0.92}
        ],
        "product": null,
        "product_category": null,
        "target_audience": null,
        "target_market": null,
        "positioning": null,
        "campaign_objective": null,
        "desired_qualities": null,
        "platform": null,
        "restrictions": null,
        "ambiguities": [],
        "unsupported_inference": [],
        "contradiction": [],
        "evidence": [
            {
                "field": "brand",
                "value": "Aurelia",
                "text": "The brand is Aurelia.",
                "block_id": "block_1",
                "source_type": "txt",
                "page_number": null,
                "section": null
            },
            {
                "field": "brand",
                "value": "Bellora",
                "text": "The brand is Bellora.",
                "block_id": "block_1",
                "source_type": "txt",
                "page_number": null,
                "section": null
            }
        ]
    }
    """

    extractor = LLMExtractor(client=FakeGroqClient(response=response))
    result = extractor.extract(blocks)

    assert [item["value"] for item in result["brand"]] == [
        "Aurelia",
        "Bellora",
    ]

