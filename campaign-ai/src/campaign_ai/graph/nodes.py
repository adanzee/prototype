from langgraph.types import interrupt

from campaign_ai.modules.requirements.service import (
    apply_operator_edits,
    understand_brief,
)
from campaign_ai.schema.requirement import (
    RequirementsResult,
    Review,
)


def make_requirements_node(extractor=None):
    def requirements_node(state):
        result = understand_brief(
            state["brief"],
            extractor,
        )

        return {
            "result": result.model_dump(mode="json"),
            "revision": 1,
        }

    return requirements_node


def confirm_node(state):
    review = interrupt({
        "result": state["result"],
        "revision": state["revision"],
    })

    result = apply_operator_edits(
        RequirementsResult.model_validate(
            state["result"]
        ),
        Review.model_validate(review),
    )

    return {
        "result": result.model_dump(mode="json"),
        "revision": state["revision"] + 1,
    }


def route_after_confirm(state):
    if state["result"]["status"] == "approved":
        return "finish"

    return "confirm"