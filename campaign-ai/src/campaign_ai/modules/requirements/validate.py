from campaign_ai.schema.requirement import (
    Question,
    RequirementsResult,
)


REQUIRED = (
    "product",
    "objective",
    "audience",
    "regions",
    "channels",
)

RECOMMENDED = (
    "tone",
    "kpis",
    "budget",
    "timeline",
)

LABELS = {
    "product": "What product or service is this campaign promoting?",
    "objective": "What is the campaign objective?",
    "audience": "Who is the target audience?",
    "regions": "Which countries or regions should the campaign target?",
    "channels": "Which channels should the campaign use?",
    "tone": "What tone should the campaign use?",
    "kpis": "Which KPIs and targets will measure success?",
    "budget": "What is the budget, including currency?",
    "timeline": "What is the campaign timeline?",
}


def validate_result(
    result: RequirementsResult,
) -> RequirementsResult:
    result = result.model_copy(deep=True)
    req = result.requirements

    result.missing_fields = [
        name
        for name in REQUIRED
        if not getattr(req, name)
    ]

    result.recommended_fields = [
        name
        for name in RECOMMENDED
        if not getattr(req, name)
    ]

    result.questions = [
        Question(
            id=f"missing:{name}",
            field=name,
            text=LABELS[name],
            blocking=True,
        )
        for name in result.missing_fields
    ]

    result.questions += [
        Question(
            id=f"recommended:{name}",
            field=name,
            text=LABELS[name],
            blocking=False,
        )
        for name in result.recommended_fields
    ]

    for index, conflict in enumerate(result.contradictions):
        key = f"conflict:{index}"

        if not result.resolutions.get(key, "").strip():
            result.questions.append(
                Question(
                    id=key,
                    field=",".join(conflict.fields),
                    text=conflict.description,
                    blocking=True,
                )
            )

    # Rule checks always use the current edited record.
    if (
        req.start_date
        and req.end_date
        and req.start_date > req.end_date
    ):
        result.questions.append(
            Question(
                id="rule:date_order",
                field="start_date,end_date",
                text="Start date must not be after end date.",
                blocking=True,
            )
        )

    overlap = sorted(
        set(req.channels) & set(req.excluded_channels)
    )

    if overlap:
        result.questions.append(
            Question(
                id="rule:channel_overlap",
                field="channels,excluded_channels",
                text=(
                    "Channels are both included and excluded: "
                    + ", ".join(overlap)
                ),
                blocking=True,
            )
        )

    result.status = "needs_review"

    return result