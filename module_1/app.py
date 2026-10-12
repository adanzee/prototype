
import tempfile
from pathlib import Path

import streamlit as st

from information_extraction.document_parser import DocumentParser, TextBlock
from information_extraction.extractor_pipeline import ExtractorPipeline


st.set_page_config(
    page_title="Campaign Requirements Extractor",
    page_icon="🧠",
    layout="wide",
)

st.title("Campaign Requirements Extractor")
st.write(
    "Extract explicitly stated campaign requirements from a brief "
    "and inspect their supporting evidence."
)

input_mode = st.radio(
    "Choose your input method",
    ["Paste text", "Upload a file"],
    horizontal=True,
)

blocks = []

if input_mode == "Paste text":
    brief_text = st.text_area(
        "Campaign brief",
        placeholder=(
            "Example: Aurelia is launching a premium floral perfume "
            "for women aged 22–35 in the UAE. The campaign aims to "
            "increase brand awareness on Instagram and TikTok."
        ),
        height=250,
    )

    if st.button("Extract requirements", type="primary"):
        if not brief_text.strip():
            st.error("Please enter a campaign brief.")
            st.stop()

        paragraphs = [
            paragraph.strip()
            for paragraph in brief_text.split("\n\n")
            if paragraph.strip()
        ]

        blocks = [
            TextBlock(
                block_id=f"block_{index + 1}",
                text=paragraph,
                source_type="text",
                page_number=None,
            )
            for index, paragraph in enumerate(paragraphs)
        ]

elif input_mode == "Upload a file":
    uploaded_file = st.file_uploader(
        "Upload a campaign brief",
        type=["txt", "docx", "pdf"],
    )

    if st.button("Extract requirements", type="primary"):
        if uploaded_file is None:
            st.error("Please upload a TXT, DOCX, or PDF file.")
            st.stop()

        suffix = Path(uploaded_file.name).suffix.lower()

        try:
            with tempfile.NamedTemporaryFile(
                suffix=suffix,
                delete=False,
            ) as temporary_file:
                temporary_file.write(uploaded_file.getvalue())
                temporary_path = Path(temporary_file.name)

            try:
                blocks = DocumentParser().parse(temporary_path)
            finally:
                temporary_path.unlink(missing_ok=True)

        except Exception as error:
            st.error(f"Could not read the uploaded file: {error}")
            st.stop()

        if not blocks:
            st.error("No readable text was found in the uploaded file.")
            st.stop()


if blocks:
    with st.spinner("Extracting and reconciling requirements..."):
        try:
            result = ExtractorPipeline().extract(blocks)
        except Exception as error:
            st.error(f"Extraction failed: {error}")
            st.stop()

    requirements = result["requirements"]
    decisions = result["reconciliation"]

    st.success("Extraction completed.")

    st.subheader("Extracted requirements")

    display_fields = {
        "Brand": "brand",
        "Product": "product",
        "Product category": "product_category",
        "Target audience": "target_audience",
        "Target market": "target_market",
        "Positioning": "positioning",
        "Campaign objective": "campaign_objective",
        "Desired qualities": "desired_qualities",
        "Platforms": "platform",
        "Restrictions": "restrictions",
    }

    for label, field_name in display_fields.items():
        field = getattr(requirements, field_name)
        value = field.value

        with st.expander(label, expanded=value is not None):
            if value is None:
                st.write("No accepted value extracted.")
            else:
                values = value if isinstance(value, list) else [value]

                for item in values:
                    st.markdown(f"**{item.value}**")

                    if item.confidence is not None:
                        st.caption(
                            f"LLM-reported confidence: "
                            f"{item.confidence:.0%}"
                        )

                    for evidence in item.evidence:
                        st.caption(
                            f"Evidence: “{evidence.text}” "
                            f"· Source block: {evidence.block_id} "
                            f"· Method: {evidence.extraction_method}"
                        )

            decision = decisions[field_name]
            st.caption(
                f"Reconciliation: {decision['status']} — "
                f"{decision['reason']}"
            )

    st.subheader("Review required")

    if requirements.ambiguities:
        st.warning("Ambiguities and rejected or conflicting values")
        for item in requirements.ambiguities:
            st.write(f"- {item}")
    else:
        st.write("No ambiguities or reconciliation issues were reported.")

    if requirements.contradiction:
        st.warning("Contradictions")
        for item in requirements.contradiction:
            st.write(f"- {item}")

    if requirements.unsupported_inference:
        st.info("Unsupported inferences identified")
        for item in requirements.unsupported_inference:
            st.write(f"- {item}")

    with st.expander("View complete structured output"):
        st.json(requirements.model_dump(mode="json"))
