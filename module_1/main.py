
import json
from pathlib import Path

from information_extraction.document_parser import DocumentParser
from information_extraction.section_segmenter import SectionSegmenter
from information_extraction.requirement_schema import RequirementSchema
from information_extraction.extractor_pipeline import ExtractorPipeline


def main():
    file_path = input("Enter campaign brief file path: ").strip()

    try:
        blocks = DocumentParser().parse(Path(file_path))
        blocks = SectionSegmenter().segment(blocks)

        pipeline = ExtractorPipeline()
        combined_fields = pipeline.extract(blocks)

        requirements = RequirementSchema(**combined_fields)

        print("\nSchema validation successful.")
        print(f"Schema version: {requirements.schema_version}")

        print("\nExtracted campaign requirements:\n")
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
