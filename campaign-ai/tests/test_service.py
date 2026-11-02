import pytest

from campaign_ai.llm.gateway import validate_grounding
from campaign_ai.modules.requirements.service import (
    apply_operator_edits,
    clean_brief,
    understand_brief,
)
from campaign_ai.samples import SAMPLES, fixture_extract
from campaign_ai.schema.requirement import (
    Extraction,
    Requirements,
    Review,
)


@pytest.mark.parametrize(
    "brief",
    ["", "   ", None, "\x00hi"],
)
def test_invalid_input(brief):
    with pytest.raises(ValueError):
        clean_brief(brief)


def test_size_and_cleaning():
    assert (
        clean_brief("  a\r\nb\rc  ")
        == "a\nb\nc"
    )

    assert clean_brief(
        "abc",
        max_chars=3,
    ) == "abc"

    with pytest.raises(ValueError):
        clean_brief(
            "abcd",
            max_chars=3,
        )


def test_unknown_and_bad_edits():
    result = understand_brief(
        next(iter(SAMPLES.values())),
        fixture_extract,
    )

    invalid_edits = [
        {"invented": "value"},
        {"regions": "UAE"},
        {"channels": [3]},
        {"product": 12},
    ]

    for edits in invalid_edits:
        with pytest.raises(ValueError):
            apply_operator_edits(
                result,
                Review(edits=edits),
            )

    with pytest.raises(ValueError):
        apply_operator_edits(
            result,
            Review(
                resolutions={
                    "conflict:99": "yes",
                }
            ),
        )


def test_edits_do_not_mutate_original_and_replace_evidence():
    result = understand_brief(
        next(iter(SAMPLES.values())),
        fixture_extract,
    )

    saved = apply_operator_edits(
        result,
        Review(
            edits={
                "product": "Updated product",
                "regions": ["UAE"],
            }
        ),
    )

    assert result.requirements.regions == []

    assert (
        saved.operator_edits["product"]
        == "Updated product"
    )

    assert all(
        item.field != "product"
        for item in saved.evidence
    )

    assert any(
        item.field == "product"
        for item in result.evidence
    )


def test_unquoted_fields_and_fabricated_quotes_rejected():
    with pytest.raises(
        ValueError,
        match="Missing evidence",
    ):
        validate_grounding(
            Extraction(
                requirements=Requirements(
                    product="fake"
                )
            ),
            "brief",
        )

    extraction = fixture_extract(
        next(iter(SAMPLES.values()))
    )

    extraction.evidence[0].quote = (
        "fabricated quotation"
    )

    with pytest.raises(
        ValueError,
        match="not found",
    ):
        validate_grounding(
            extraction,
            "brief",
        )


def test_fixture_rejects_arbitrary_text():
    with pytest.raises(
        ValueError,
        match="only bundled",
    ):
        fixture_extract("An arbitrary brief")