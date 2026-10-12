
from information_extraction.document_parser import TextBlock
from information_extraction.rule_extractor import RuleExtractor
from information_extraction.llm_extractor import LLMExtractor
from information_extraction.reconciliation import reconcile, ORDINARY_FIELDS
from information_extraction.requirement_schema import (
    Evidence,
    RequirementField,
    RequirementSchema,
    RequirementValue,
)


class ExtractorPipeline:
    def __init__(self, llm_extractor: LLMExtractor | None = None):
        self.rule_extractor = RuleExtractor()
        self.llm_extractor = llm_extractor or LLMExtractor()

    def extract(self, blocks: list[TextBlock]) -> dict:
        if not blocks:
            raise ValueError("Cannot extract requirements from an empty brief.")

        # Run both extractors independently.
        rule_fields = self.rule_extractor.extract_all_labeled_fields(blocks)
        llm_result = self.llm_extractor.extract(blocks)

        # Apply the reconciliation policy.
        decisions = reconcile(rule_fields, llm_result)

        # Build validated schema fields from accepted values only.
        schema_fields = {}

        for field_name in ORDINARY_FIELDS:
            decision = decisions[field_name]
            accepted_values = []

            for item in decision["values"]:
                evidence_items = [
                    Evidence(
                        text=e["text"],
                        block_id=e["block_id"],
                        source_type=e["source_type"],
                        page_number=e["page_number"],
                        section=e["section"],
                        extraction_method=e.get("extraction_method", "llm"),
                    )
                    for e in item["evidence"]
                ]

                if not evidence_items:
                    raise ValueError(
                        f"Accepted value for {field_name!r} has no evidence."
                    )

                accepted_values.append(
                    RequirementValue(
                        value=item["value"],
                        confidence=item["confidence"],
                        evidence=evidence_items,
                    )
                )

            if not accepted_values:
                schema_fields[field_name] = RequirementField()
                continue

            field_value = (
                accepted_values[0]
                if len(accepted_values) == 1
                else accepted_values
            )

            evidence_by_key = {
                (e.block_id, e.text, e.extraction_method): e
                for item in accepted_values
                for e in item.evidence
            }

            schema_fields[field_name] = RequirementField(
                value=field_value,
                evidence=list(evidence_by_key.values()),
            )

        # Keep conflicts and rejections visible for later resolution.
        unresolved = [
            f"{field}: {decision['reason']}"
            for field, decision in decisions.items()
            if decision["status"] in {"needs_resolution", "rejected"}
        ]

        schema = RequirementSchema(
            **schema_fields,
            ambiguities=llm_result["ambiguities"] + unresolved,
            unsupported_inference=llm_result["unsupported_inference"],
            contradiction=llm_result["contradiction"],
        )

        return {
            "requirements": schema,
            "reconciliation": decisions,
        }
