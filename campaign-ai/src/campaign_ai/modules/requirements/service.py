from campaign_ai.config import get_settings
from campaign_ai.modules.requirements.extract import extract_requirements
from campaign_ai.modules.requirements.validate import validate_result
from campaign_ai.schema.requirement import (
    Requirements,
    RequirementsResult,
    Review,
)


class ApprovalBlocked(ValueError):
    pass


def clean_brief(
    brief: str,
    max_chars: int | None = None,
) -> str:
    limit = (
        max_chars
        if max_chars is not None
        else get_settings().max_brief_chars
    )

    if not isinstance(brief, str) or not brief.strip():
        raise ValueError("Brief must contain text")

    if len(brief) > limit:
        raise ValueError(
            f"Brief exceeds the {limit} character limit"
        )

    if "\x00" in brief:
        raise ValueError("Brief contains a null character")

    return (
        brief
        .replace("\r\n", "\n")
        .replace("\r", "\n")
        .strip()
    )


def understand_brief(
    brief: str,
    extractor=None,
) -> RequirementsResult:
    cleaned = clean_brief(brief)

    extraction = (
        extractor or extract_requirements
    )(cleaned)

    from campaign_ai.llm.gateway import validate_grounding

    validate_grounding(extraction, cleaned)

    result = RequirementsResult(
        **extraction.model_dump()
    )

    return validate_result(result)


def apply_operator_edits(
    result: RequirementsResult,
    review: Review,
) -> RequirementsResult:
    unknown = (
        set(review.edits)
        - Requirements.model_fields.keys()
    )

    if unknown:
        raise ValueError(
            "Unknown edit fields: "
            + ", ".join(sorted(unknown))
        )

    updated = result.model_copy(deep=True)

    updated.requirements = Requirements.model_validate({
        **result.requirements.model_dump(),
        **review.edits,
    })

    changed = {
        key: getattr(updated.requirements, key)
        for key in review.edits
        if (
            getattr(updated.requirements, key)
            != getattr(result.requirements, key)
        )
    }

    # Reopen a conflict if an affected field changes again.
    for index, conflict in enumerate(updated.contradictions):
        if set(conflict.fields) & changed.keys():
            updated.resolutions.pop(
                f"conflict:{index}",
                None,
            )

    allowed_resolution_ids = {
        f"conflict:{index}"
        for index in range(len(updated.contradictions))
    }

    for key, note in review.resolutions.items():
        if (
            key not in allowed_resolution_ids
            or not note.strip()
        ):
            raise ValueError(
                "Conflict resolutions need a known conflict ID "
                "and a nonempty explanation"
            )

        updated.resolutions[key] = note.strip()

    serialized = updated.requirements.model_dump(mode="json")

    updated.operator_edits.update({
        key: serialized[key]
        for key in changed
    })

    # Old model evidence must not be attributed to human edits.
    updated.evidence = [
        item
        for item in updated.evidence
        if item.field not in changed
    ]

    updated = validate_result(updated)

    if review.approve:
        if any(
            question.blocking
            for question in updated.questions
        ):
            raise ApprovalBlocked(
                "Resolve all required fields and blocking "
                "questions before approval"
            )

        updated.status = "approved"

    return updated