
from types import SimpleNamespace

from module_1.information_extraction.reconciliation import reconcile_field
from module_1.information_extraction.requirement_schema import (
    RequirementField,
    RequirementValue,
)


def make_rule_field(value=None):
    if value is None:
        return RequirementField()

    item = RequirementValue(
        value=value,
        evidence=[
            {
                "text": f"Brand: {value}",
                "block_id": "block_1",
                "source_type": "txt",
                "page_number": None,
                "section": None,
                "extraction_method": "rule",
            }
        ],
    )
    return RequirementField(value=item)


def make_llm_field(value=None, confidence=0.95):
    if value is None:
        return None

    return [{"value": value, "confidence": confidence}]


def test_matching_values_are_accepted():
    result = reconcile_field(
        make_rule_field("Aurelia"),
        make_llm_field("Aurelia", 0.80),
        field_name="brand",
    )

    assert result["status"] == "accepted"


def test_high_confidence_llm_only_value_is_accepted():
    result = reconcile_field(
        make_rule_field(),
        make_llm_field("Aurelia", 0.90),
        field_name="brand",
    )

    assert result["status"] == "accepted"


def test_rule_only_value_is_rejected():
    result = reconcile_field(
        make_rule_field("Aurelia"),
        make_llm_field(),
        field_name="brand",
    )

    assert result["status"] == "rejected"


def test_different_values_flag_the_entire_field():
    result = reconcile_field(
        make_rule_field("Aurelia"),
        make_llm_field("Bellora", 0.99),
        field_name="brand",
    )

    assert result["status"] == "needs_resolution"
    assert result["values"] == []
    assert result["rule_candidates"][0]["value"] == "Aurelia"
    assert result["llm_candidates"][0]["value"] == "Bellora"


def test_low_confidence_llm_only_value_is_rejected():
    result = reconcile_field(
        make_rule_field(),
        make_llm_field("Aurelia", 0.89),
        field_name="brand",
    )

    assert result["status"] == "rejected"


def test_missing_values_are_unresolved():
    result = reconcile_field(
        make_rule_field(),
        make_llm_field(),
        field_name="brand",
    )

    assert result["status"] == "unresolved"


def test_accepted_llm_value_preserves_matching_evidence():
    rule_field = make_rule_field()

    llm_field = make_llm_field("Aurelia", 0.95)

    llm_evidence = [
        {
            "field": "brand",
            "value": "Aurelia",
            "text": "Brand: Aurelia",
            "block_id": "block_1",
            "source_type": "txt",
            "page_number": None,
            "section": None,
        }
    ]

    result = reconcile_field(
        rule_field,
        llm_field,
        field_name="brand",
        llm_evidence=llm_evidence,
    )

    assert result["status"] == "accepted"
    assert result["values"][0]["value"] == "Aurelia"
    assert result["values"][0]["evidence"] == llm_evidence


def test_matching_values_preserve_evidence_from_both_extractors():
    llm_evidence = [
        {
            "field": "brand",
            "value": "Aurelia",
            "text": "Our brand is Aurelia.",
            "block_id": "block_2",
            "source_type": "txt",
            "page_number": None,
            "section": None,
        }
    ]

    result = reconcile_field(
        make_rule_field("Aurelia"),
        make_llm_field("Aurelia", confidence=0.95),
        field_name="brand",
        llm_evidence=llm_evidence,
    )

    assert result["status"] == "accepted"

    evidence = result["values"][0]["evidence"]

    assert any(
        item.get("extraction_method") == "rule"
        for item in evidence
    )
    assert any(
        item.get("block_id") == "block_2"
        for item in evidence
    )

