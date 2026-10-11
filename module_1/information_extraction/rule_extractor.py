
import re

from information_extraction.document_parser import TextBlock
from information_extraction.requirement_schema import (
    Evidence,
    RequirementField,
    RequirementValue,
)


class RuleExtractor:
    FIELD_LABELS = {
        "brand": ["brand", "brand name"],
        "product": ["product", "product name"],
        "product_category": ["product category", "category"],
        "target_audience": ["target audience", "audience"],
        "target_market": ["target market", "geographic market"],
        "positioning": ["positioning", "brand positioning"],
        "campaign_objective": ["campaign objective", "campaign goal"],
        "desired_qualities": ["desired qualities", "desired attributes"],
        "platform": ["platform", "platforms", "channels"],
        "restrictions": ["restrictions", "constraints", "limitations"],
    }

    def _make_value(
        self,
        value: str,
        block: TextBlock,
        matched_text: str,
    ) -> RequirementValue:
        return RequirementValue(
            value=value,
            evidence=[
                Evidence(
                    text=matched_text,
                    block_id=block.block_id,
                    source_type=block.source_type,
                    page_number=block.page_number,
                    section=block.section,
                    extraction_method="rule",
                )
            ],
        )

    def _make_field(
        self,
        values: list[RequirementValue],
    ) -> RequirementField:
        if not values:
            return RequirementField(value=None, evidence=[])

        unique_values = {}
        for item in values:
            unique_values.setdefault(item.value.casefold(), item)

        values = list(unique_values.values())

        evidence_by_key = {}
        for item in values:
            for evidence in item.evidence:
                evidence_by_key[
                    (evidence.block_id, evidence.text)
                ] = evidence

        return RequirementField(
            value=values[0] if len(values) == 1 else values,
            evidence=list(evidence_by_key.values()),
        )

    
    def _split_field_values(
        self,
        field_name: str,
        value: str,
    ) -> list[str]:
        if field_name == "platform":
            return [
                item.strip()
                for item in re.split(r"\s*[,;]\s*", value)
                if item.strip()
            ]

        return [value.strip()] if value.strip() else []


    def extract_labeled_field(
        self,
        blocks: list[TextBlock],
        field_name: str,
    ) -> RequirementField:
        if field_name not in self.FIELD_LABELS:
            raise ValueError(f"Unsupported field: {field_name}")

        labels = sorted(
            self.FIELD_LABELS[field_name],
            key=len,
            reverse=True,
        )
        label_pattern = "|".join(
            re.escape(label) for label in labels
        )

        pattern = re.compile(
            rf"^\s*(?:{label_pattern})\s*:\s*(.+?)\s*$",
            re.IGNORECASE,
        )

        extracted = []

        for block in blocks:
            for line in block.text.splitlines():
                match = pattern.match(line)

                if match:
                    value = match.group(1).strip()

                    if value:
                        for item in self._split_field_values(field_name, value):
                            extracted.append(
                            self._make_value(item, block, line.strip()))
        return self._make_field(extracted)

    def extract_all_labeled_fields(
        self,
        blocks: list[TextBlock],
    ) -> dict[str, RequirementField]:
        return {
            field_name: self.extract_labeled_field(blocks, field_name)
            for field_name in self.FIELD_LABELS
        }
