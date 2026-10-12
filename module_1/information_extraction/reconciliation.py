
from typing import Any


LLM_CONFIDENCE_THRESHOLD = 0.90

ORDINARY_FIELDS = {
    "brand",
    "product",
    "product_category",
    "target_audience",
    "target_market",
    "positioning",
    "campaign_objective",
    "desired_qualities",
    "platform",
    "restrictions",
}


def _rule_values(field: Any) -> list[dict]:
    """Convert a rule extractor field into a list of value dictionaries."""
    raw_value = field.value

    if raw_value is None:
        return []

    items = raw_value if isinstance(raw_value, list) else [raw_value]

    return [
        {
            "value": item.value.strip(),
            "confidence": item.confidence,
            "evidence": [e.model_dump() for e in item.evidence],
        }
        for item in items
    ]




def _llm_values(
    field: Any,
    evidence_items: list[dict] | None = None,
    field_name: str | None = None,
) -> list[dict]:
    """Normalize LLM values and attach matching field-specific evidence."""
    if field is None:
        return []

    evidence_items = evidence_items or []
    normalized = []

    for item in field:
        value = item["value"].strip()

        matching_evidence = [
            evidence
            for evidence in evidence_items
            if evidence["field"] == field_name
            and evidence["value"].strip().casefold() == value.casefold()
        ]

        normalized.append({
            "value": value,
            "confidence": item["confidence"],
            "evidence": matching_evidence,
        })

    return normalized




def _value_set(values: list[dict]) -> set[str]:
    """Compare values without case or surrounding-whitespace differences."""
    return {item["value"].strip().casefold() for item in values}



def reconcile_field(
    rule_field: Any,
    llm_field: Any,
    field_name: str,
    llm_evidence: list[dict] | None = None,
) -> dict:
    """Apply reconciliation policy while preserving evidence."""
    rule_values = _rule_values(rule_field)
    llm_values = _llm_values(llm_field, llm_evidence, field_name)

    rule_set = _value_set(rule_values)
    llm_set = _value_set(llm_values)

    if rule_set and llm_set:

        if rule_set == llm_set:
            llm_by_value = {
                item["value"].casefold(): item
                for item in llm_values
            }

            accepted_values = []

            for rule_item in rule_values:
                llm_item = llm_by_value[rule_item["value"].casefold()]

                combined_evidence = {}
                for evidence in (
                    rule_item["evidence"] + llm_item["evidence"]
                ):
                    key = (
                        evidence.get("block_id"),
                        evidence.get("text"),
                        evidence.get("field"),
                        evidence.get("value"),
                    )
                    combined_evidence[key] = evidence

                accepted_values.append({
                    **rule_item,
                    "confidence": llm_item["confidence"],
                    "evidence": list(combined_evidence.values()),
                })

            return {
                "status": "accepted",
                "values": accepted_values,
                "reason": "Both extractors agree; evidence from both is preserved.",
            }


        return {
            "status": "needs_resolution",
            "values": [],
            "rule_candidates": rule_values,
            "llm_candidates": llm_values,
            "reason": "Extractors disagree; the entire field is flagged.",
        }


    if rule_set and not llm_set:
        return {
            "status": "rejected",
            "values": [],
            "reason": "Rules extracted a value but the LLM did not.",
        }

    if not rule_set and llm_set:
        if all(
            item["confidence"] >= LLM_CONFIDENCE_THRESHOLD
            for item in llm_values
        ):
            return {
                "status": "accepted",
                "values": llm_values,
                "reason": "LLM-only values meet the confidence threshold.",
            }

        return {
            "status": "rejected",
            "values": [],
            "reason": "At least one LLM-only value is below the threshold.",
        }

    return {
        "status": "unresolved",
        "values": [],
        "reason": "Neither extractor found a value.",
    }



def reconcile(rule_result: dict, llm_result: dict) -> dict:
    """Reconcile all ordinary fields and pass their LLM evidence."""
    llm_evidence = llm_result.get("evidence", [])

    return {
        field: reconcile_field(
            rule_result[field],
            llm_result[field],
            field_name=field,
            llm_evidence=llm_evidence,
        )
        for field in ORDINARY_FIELDS
    }

