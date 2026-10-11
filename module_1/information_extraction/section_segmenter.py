
import re

from information_extraction.document_parser import TextBlock


class SectionSegmenter:
    SECTION_SYNONYMS = {
        "brand_overview": [
            "brand overview",
            "about the brand",
            "brand background",
            "company overview",
        ],
        "product": [
            "product",
            "product overview",
            "product description",
        ],
        "target_audience": [
            "target audience",
            "audience",
            "target consumers",
            "customer profile",
        ],
        "target_market": [
            "target market",
            "geographic market",
            "market",
            "target region",
        ],
        "campaign_objective": [
            "campaign objective",
            "objectives",
            "campaign goals",
            "goals",
        ],
        "platform": [
            "platform",
            "platforms",
            "channels",
            "marketing channels",
        ],
        "creative_direction": [
            "creative direction",
            "creative guidelines",
            "visual direction",
            "tone and style",
        ],
        "restrictions": [
            "restrictions",
            "constraints",
            "limitations",
            "things to avoid",
            "prohibited claims",
        ],
        "deliverables": [
            "deliverables",
            "required assets",
            "content requirements",
            "required content",
        ],
        "budget": [
            "budget",
            "campaign budget",
            "spending limit",
        ],
        "timeline": [
            "timeline",
            "campaign dates",
            "schedule",
            "deadline",
        ],
        "positioning": [
            "positioning",
            "brand positioning",
            "market positioning",
        ],
    }

    def __init__(self):
        self._heading_lookup = {
            self._normalize(heading): section
            for section, headings in self.SECTION_SYNONYMS.items()
            for heading in headings
        }

    def segment(self, blocks: list[TextBlock]) -> list[TextBlock]:
        segmented_blocks = []
        current_section = None

        for block in blocks:
            lines = block.text.splitlines()
            content_lines = []

            for line in lines:
                heading = self._identify_heading(line)

                if heading:
                    current_section = heading
                else:
                    content_lines.append(line)

            content = "\n".join(content_lines).strip()

            if content:
                segmented_blocks.append(
                    TextBlock(
                        block_id=block.block_id,
                        text=content,
                        source_type=block.source_type,
                        page_number=block.page_number,
                        section=current_section,
                    )
                )

        return segmented_blocks

    def _identify_heading(self, line: str) -> str | None:
        normalized = self._normalize(line)

        if not normalized:
            return None

        return self._heading_lookup.get(normalized)

    @staticmethod
    def _normalize(text: str) -> str:
        text = text.strip().lower()
        text = re.sub(r"^\s*\d+[\.\):\-]\s*", "", text)
        text = re.sub(r"[:\s]+$", "", text)
        return re.sub(r"\s+", " ", text)
