
import spacy

from information_extraction.document_parser import TextBlock
from information_extraction.requirement_schema import (
    Evidence,
    RequirementValue,
)


class NLPExtractor:
    def __init__(self, model_name: str = "en_core_web_sm"):
        self.nlp = spacy.load(model_name)

    def extract_entities(
        self,
        blocks: list[TextBlock],
    ) -> list[dict]:
        entities = []

        for block in blocks:
           for line in block.text.splitlines():
            line = line.strip()

            if not line:
                continue

            doc = self.nlp(line)

            for ent in doc.ents:
                entities.append(
                {
                    "text": ent.text,
                    "label": ent.label_,
                    "sentence": ent.sent.text,
                    "source_line": line,
                    "evidence": Evidence(
                        text=ent.text,
                        block_id=block.block_id,
                        source_type=block.source_type,
                        page_number=block.page_number,
                        section=block.section,
                        extraction_method="ner",
                    ),
                }
            )
        return entities

        
    def map_entity_to_field(self, source_line: str) -> str | None:
        label = source_line.split(":", maxsplit=1)[0].strip().casefold()

        label_to_field = {
            "brand": "brand",
            "brand name": "brand",
            "product": "product",
            "product name": "product",
            "product category": "product_category",
            "category": "product_category",
            "target audience": "target_audience",
            "audience": "target_audience",
            "target market": "target_market",
            "geographic market": "target_market",
            "positioning": "positioning",
            "brand positioning": "positioning",
            "campaign objective": "campaign_objective",
            "campaign goal": "campaign_objective",
            "platform": "platform",
            "platforms": "platform",
            "channels": "platform",
            "restrictions": "restrictions",
            "constraints": "restrictions",
            "limitations": "restrictions",
        }

        return label_to_field.get(label)

    
    def extract_mapped_entities(
        self,
        blocks: list[TextBlock],
    ) -> dict[str, list[RequirementValue]]:
        mapped: dict[str, list[RequirementValue]] = {}

        for entity in self.extract_entities(blocks):
            field_name = self.map_entity_to_field(entity["source_line"])

            if field_name is None:
                continue

            mapped.setdefault(field_name, []).append(
                RequirementValue(
                    value=entity["text"],
                    evidence=[entity["evidence"]],
                )
            )

        return mapped



