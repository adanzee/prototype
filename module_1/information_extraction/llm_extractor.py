
import json

from .llm_client import GroqClient


class LLMExtractor:
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

    LIST_FIELDS = {
        "ambiguities",
        "unsupported_inference",
        "contradiction",
        "evidence",
    }

    def __init__(self, client: GroqClient | None = None):
        self.client = client or GroqClient()

    def extract(self, blocks) -> dict:
        source_blocks = [
            {
                "block_id": block.block_id,
                "text": block.text,
                "source_type": block.source_type,
                "page_number": block.page_number,
                "section": block.section,
            }
            for block in blocks
        ]

        if not source_blocks:
            raise ValueError(
                "Cannot extract requirements from an empty brief."
            )

        prompt = """
You are a strict information extraction component for campaign briefs.

Extract only campaign requirements explicitly supported by the source.
Do not invent values or infer unstated design requirements.

If a field has no explicitly supported value, return null.
If a statement is ambiguous or contradictory, record it in the
appropriate list.

Return exactly one complete JSON object with these fields:
brand, product, product_category, target_audience, target_market,
positioning, campaign_objective, desired_qualities, platform,
restrictions, ambiguities, unsupported_inference, contradiction,
evidence.

Every ordinary field must be null or a list of objects.
Every object must contain exactly:
- "value": a non-empty extracted string
- "confidence": a number between 0 and 1

Confidence represents your estimate of how directly the source supports
the value. It does not justify unsupported inference.

Each evidence item must contain exactly:
- "field"
- "value"
- "text"
- "block_id"
- "source_type"
- "page_number"
- "section"

Evidence requirements:
1. Every extracted value must have at least one evidence item.
2. Every evidence item must correspond to an extracted field and value.
3. Evidence text must be copied exactly from a supplied source block.
4. block_id and all metadata must match that source block exactly.
5. Evidence must directly support the associated field and value.
6. Do not omit evidence for any item, including items in
   desired_qualities or platform.
7. Do not create evidence for values that you did not extract.

Use null for ordinary fields with no supported values.
Use empty lists for ambiguities, unsupported_inference, contradiction,
and evidence when appropriate.

Do not include Markdown fences or explanatory text.
Do not copy values from this prompt's examples.
Return all required fields, even when they contain null or empty lists.

Required structure:
{
  "brand": null,
  "product": null,
  "product_category": null,
  "target_audience": null,
  "target_market": null,
  "positioning": null,
  "campaign_objective": null,
  "desired_qualities": null,
  "platform": null,
  "restrictions": null,
  "ambiguities": [],
  "unsupported_inference": [],
  "contradiction": [],
  "evidence": []
}

Source blocks:
""" + json.dumps(source_blocks, ensure_ascii=False)


        last_error = None

        for attempt in range(2):
            retry_prompt = prompt

            if attempt == 1:
                retry_prompt += (
                    "\n\nRETRY INSTRUCTIONS:\n"
                    "Your previous response failed validation or "
                    "the request failed.\n"
                    "Return a complete JSON object containing every "
                    "required field.\n"
                    "Ensure every extracted value has matching evidence.\n"
                    "Ensure every evidence item references an extracted "
                    "value and a real source block.\n"
                    "Copy evidence text and metadata exactly from the "
                    "provided source blocks.\n"
                    "Do not omit fields or weaken any requirements."
                )

            try:
                response = self.client.generate(retry_prompt)
                result = json.loads(response)
                self._validate_structure(result)
                self.validate_evidence(result, blocks)
                return result

            except Exception as error:
                # Retry transient API errors and invalid model output.
                last_error = error

        raise ValueError(
            "Groq failed to return a valid extraction after "
            f"2 attempts: {last_error}"
        ) from last_error


    def _validate_structure(self, result: dict) -> None:
        if not isinstance(result, dict):
            raise ValueError(
                "The LLM response must be a JSON object."
            )

        expected_fields = self.ORDINARY_FIELDS | self.LIST_FIELDS

        missing_fields = expected_fields - result.keys()
        unexpected_fields = result.keys() - expected_fields

        if missing_fields:
            raise ValueError(
                f"LLM response is missing fields: "
                f"{sorted(missing_fields)}"
            )

        if unexpected_fields:
            raise ValueError(
                f"LLM response contains unexpected fields: "
                f"{sorted(unexpected_fields)}"
            )

        for field in self.ORDINARY_FIELDS:
            values = result[field]

            if values is None:
                continue

            if not isinstance(values, list):
                raise ValueError(
                    f"Field {field!r} must be a list or null."
                )

            seen_values = set()

            for item in values:
                if not isinstance(item, dict):
                    raise ValueError(
                        f"Each item in {field!r} must be an object."
                    )

                if set(item.keys()) != {"value", "confidence"}:
                    raise ValueError(
                        f"Each item in {field!r} must contain "
                        "'value' and 'confidence' only."
                    )

                extracted_value = item["value"]
                confidence = item["confidence"]

                if (
                    not isinstance(extracted_value, str)
                    or not extracted_value.strip()
                ):
                    raise ValueError(
                        f"Field {field!r} contains an invalid value."
                    )

                if (
                    isinstance(confidence, bool)
                    or not isinstance(confidence, (int, float))
                    or not 0 <= confidence <= 1
                ):
                    raise ValueError(
                        f"Confidence for {field!r} must be a number "
                        "between 0 and 1."
                    )

                normalized_value = extracted_value.strip().casefold()

                if normalized_value in seen_values:
                    raise ValueError(
                        f"Field {field!r} contains duplicate values."
                    )

                seen_values.add(normalized_value)

        for field in self.LIST_FIELDS:
            if not isinstance(result[field], list):
                raise ValueError(
                    f"Field {field!r} must be a list."
                )

    def validate_evidence(self, result: dict, blocks) -> None:
        blocks_by_id = {
            block.block_id: block
            for block in blocks
        }

        evidence_items = result.get("evidence")

        if not isinstance(evidence_items, list):
            raise ValueError("Evidence must be a list.")

        evidenced_values = set()

        for item in evidence_items:
            if not isinstance(item, dict):
                raise ValueError(
                    "Each evidence item must be an object."
                )

            required_evidence_fields = {
                "field",
                "value",
                "text",
                "block_id",
                "source_type",
                "page_number",
                "section",
            }

            if set(item.keys()) != required_evidence_fields:
                raise ValueError(
                    "Evidence item contains missing or unexpected fields."
                )

            field = item["field"]
            value = item["value"]
            block_id = item["block_id"]
            evidence_text = item["text"]

            if field not in self.ORDINARY_FIELDS:
                raise ValueError(
                    f"Unknown evidence field: {field!r}"
                )

            if not all(
                isinstance(text, str) and text.strip()
                for text in (value, evidence_text, block_id)
            ):
                raise ValueError(
                    "Evidence contains missing or invalid text."
                )

            block = blocks_by_id.get(block_id)

            if block is None:
                raise ValueError(
                    f"Evidence references unknown block: {block_id}"
                )

            if evidence_text not in block.text:
                raise ValueError(
                    f"Evidence text does not match source block: "
                    f"{block_id}"
                )

            if item["source_type"] != block.source_type:
                raise ValueError(
                    f"Evidence source type mismatch: {block_id}"
                )

            if item["page_number"] != block.page_number:
                raise ValueError(
                    f"Evidence page number mismatch: {block_id}"
                )

            if item["section"] != block.section:
                raise ValueError(
                    f"Evidence section mismatch: {block_id}"
                )

            field_values = result[field]

            if field_values is None:
                raise ValueError(
                    f"Evidence exists for null field {field!r}."
                )

            if not any(
                candidate["value"].strip().casefold() == value.strip().casefold()
                for candidate in field_values
            ):
                raise ValueError(
                    f"Evidence value {value!r} is not present "
                    f"in {field!r}."
                )

            evidenced_values.add((field, value))

        for field in self.ORDINARY_FIELDS:
            field_values = result[field]

            if field_values is None:
                continue

            for item in field_values:
                extracted_value = item["value"]

                if (field, extracted_value) not in evidenced_values:
                    raise ValueError(
                        f"Missing evidence for {field!r}: "
                        f"{extracted_value!r}"
                    )
