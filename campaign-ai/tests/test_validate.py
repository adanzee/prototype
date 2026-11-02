from datetime import date

import pytest

from campaign_ai.modules.requirements.service import (
    ApprovalBlocked,
    apply_operator_edits,
    understand_brief,
)
from campaign_ai.modules.requirements.validate import (
    validate_result,
)
from campaign_ai.samples import SAMPLES, fixture_extract
from campaign_ai.schema.requirement import (
    Requirements,
    Review,
)


@pytest.mark.parametrize(
    "field",
    [
        "product",
        "objective",
        "audience",
        "regions",
        "channels",
    ],
)
def test_each_required_field_blocks_approval(field):
    result = understand_brief(
        list(SAMPLES.values())[1],
        fixture_extract,
    )

    blank = (
        []
        if field in ("regions", "channels")
        else "   "
    )

    with pytest.raises(ApprovalBlocked):
        apply_operator_edits(
            result,
            Review(
                edits={field: blank},
                approve=True,
            ),
        )


def test_recommended_fields_do_not_block():
    result = understand_brief(
        list(SAMPLES.values())[1],
        fixture_extract,
    )

    approved = apply_operator_edits(
        result,
        Review(
            edits={
                "tone": [],
                "budget": None,
                "kpis": [],
                "timeline": None,
            },
            approve=True,
        ),
    )

    assert approved.status == "approved"
    assert len(approved.recommended_fields) == 4


def test_normalization():
    req = Requirements(
        channels=[
            "IG",
            "instagram",
            "FB",
            "YT",
            "Tik Tok",
            "  ",
        ],
        product="  ",
    )

    assert req.channels == [
        "instagram",
        "facebook",
        "youtube",
        "tiktok",
    ]

    assert req.product is None


def test_deterministic_contradictions():
    result = understand_brief(
        list(SAMPLES.values())[1],
        fixture_extract,
    )

    result.requirements.start_date = date(2026, 12, 2)
    result.requirements.end_date = date(2026, 11, 1)
    result.requirements.excluded_channels = ["instagram"]

    checked = validate_result(result)

    blocking_ids = {
        question.id
        for question in checked.questions
        if question.blocking
    }

    assert blocking_ids == {
        "rule:date_order",
        "rule:channel_overlap",
    }

    with pytest.raises(ApprovalBlocked):
        apply_operator_edits(
            result,
            Review(approve=True),
        )


def test_conflict_needs_resolution_and_reopens():
    result = understand_brief(
        list(SAMPLES.values())[2],
        fixture_extract,
    )

    with pytest.raises(ApprovalBlocked):
        apply_operator_edits(
            result,
            Review(
                edits={"tone": ["formal"]},
                approve=True,
            ),
        )

    saved = apply_operator_edits(
        result,
        Review(
            edits={"tone": ["formal"]},
            resolutions={
                "conflict:0": (
                    "Operator confirmed formal tone."
                ),
            },
        ),
    )

    assert not any(
        question.blocking
        for question in saved.questions
    )

    changed = apply_operator_edits(
        saved,
        Review(
            edits={"tone": ["playful"]},
        ),
    )

    assert any(
        question.id == "conflict:0"
        for question in changed.questions
    )

    approved = apply_operator_edits(
        saved,
        Review(approve=True),
    )

    assert approved.status == "approved"