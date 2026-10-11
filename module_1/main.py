
import json
from pathlib import Path

from information_extraction.document_parser import DocumentParser
from information_extraction.section_segmenter import SectionSegmenter
from information_extraction.rule_extractor import RuleExtractor
from information_extraction.requirement_schema import RequirementSchema
from information_extraction.nlp_extractor import NLPExtractor


def main():
    file_path = input("Enter campaign brief file path: ").strip()

    try:
        blocks = DocumentParser().parse(Path(file_path))
        blocks = SectionSegmenter().segment(blocks)

        entities = NLPExtractor().extract_entities(blocks)

        print("\nNLP entities:\n")
        for entity in entities:
           print(
            f"Text: {entity['text']} | "
            f"Label: {entity['label']} | "
            f"Sentence: {entity['sentence']} | "
            f"Section: {entity['evidence'].section}"
            )

        extractor = RuleExtractor()
        extracted_fields = extractor.extract_all_labeled_fields(blocks)

        requirements = RequirementSchema(**extracted_fields)

        print("\nExtracted requirements:\n")
        print(
            json.dumps(
                requirements.model_dump(mode="json"),
                indent=2,
                ensure_ascii=False,
            )
        )

    except (FileNotFoundError, ValueError) as error:
        print(f"Error: {error}")


if __name__ == "__main__":
    main()
