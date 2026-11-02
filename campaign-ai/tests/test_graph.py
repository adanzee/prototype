import pytest

from langgraph.checkpoint.memory import InMemorySaver
from langgraph.types import Command

from campaign_ai.graph.builder import build_graph
from campaign_ai.modules.requirements.service import ApprovalBlocked
from campaign_ai.schema.requirement import (
    Requirements,
    RequirementsResult,
)


def fake_understand(_text, extractor=None):
    from campaign_ai.modules.requirements.validate import validate_result

    return validate_result(
        RequirementsResult(
            requirements=Requirements(
                product="Sneakers",
                objective="awareness",
                audience="Gen Z",
                channels=["instagram"],
                regions=[],
            )
        )
    )


def start(graph, thread="t1"):
    config = {
        "configurable": {
            "thread_id": thread,
        }
    }

    output = graph.invoke(
        {
            "agency_id": "a",
            "client_brand_id": "b",
            "brief": "Test campaign brief",
        },
        config,
    )

    return config, output


def test_pauses_then_completes(monkeypatch):
    monkeypatch.setattr(
        "campaign_ai.graph.nodes.understand_brief",
        fake_understand,
    )

    graph = build_graph(
        checkpointer=InMemorySaver()
    )

    config, output = start(graph)

    assert "__interrupt__" in output

    paused_result = (
        output["__interrupt__"][0].value["result"]
    )

    assert paused_result["status"] == "needs_review"
    assert "regions" in paused_result["missing_fields"]

    output = graph.invoke(
        Command(
            resume={
                "approve": True,
                "edits": {
                    "regions": ["Germany"],
                },
            }
        ),
        config,
    )

    assert output["result"]["status"] == "approved"

    assert (
        output["result"]["requirements"]["regions"]
        == ["Germany"]
    )

    assert not graph.get_state(config).next


def test_cannot_approve_while_incomplete(monkeypatch):
    monkeypatch.setattr(
        "campaign_ai.graph.nodes.understand_brief",
        fake_understand,
    )

    graph = build_graph(
        checkpointer=InMemorySaver()
    )

    config, _ = start(graph)

    with pytest.raises(ApprovalBlocked):
        graph.invoke(
            Command(
                resume={
                    "approve": True,
                    "edits": {},
                }
            ),
            config,
        )

    state = graph.get_state(config)

    assert state.values["result"]["status"] == "needs_review"

    assert (
        state.values["result"]["requirements"]["regions"]
        == []
    )