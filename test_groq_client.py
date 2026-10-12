from module_1.information_extraction.document_parser import DocumentParser
from module_1.information_extraction.llm_extractor import LLMExtractor


def main():
    parser = DocumentParser()
    blocks = parser.parse("module_1/sample_brief.txt")

    extractor = LLMExtractor()
    result = extractor.extract(blocks)

    extractor.validate_evidence(result, blocks)

    print(result)


if __name__ == "__main__":
    main()