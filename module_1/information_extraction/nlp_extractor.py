
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
