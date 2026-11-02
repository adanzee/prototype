from contextlib import contextmanager

from langgraph.checkpoint.memory import InMemorySaver
from langgraph.graph import END, START, StateGraph

from campaign_ai.config import get_settings
from campaign_ai.graph.nodes import (
    confirm_node,
    make_requirements_node,
    route_after_confirm,
)
from campaign_ai.graph.state import CampaignState


def build_graph(
    checkpointer=None,
    extractor=None,
):
    builder = StateGraph(CampaignState)

    builder.add_node(
        "requirements",
        make_requirements_node(extractor),
    )

    builder.add_node(
        "confirm",
        confirm_node,
    )

    builder.add_node(
        "finish",
        lambda state: {},
    )

    builder.add_edge(START, "requirements")
    builder.add_edge("requirements", "confirm")

    builder.add_conditional_edges(
        "confirm",
        route_after_confirm,
    )

    builder.add_edge("finish", END)

    saver = (
        checkpointer
        if checkpointer is not None
        else InMemorySaver()
    )

    return builder.compile(checkpointer=saver)


@contextmanager
def graph_context(
    settings=None,
    extractor=None,
):
    settings = settings or get_settings()

    database_url = (
        settings.database_url.get_secret_value()
    )

    if database_url:
        from langgraph.checkpoint.postgres import PostgresSaver

        with PostgresSaver.from_conn_string(
            database_url
        ) as saver:
            saver.setup()

            yield build_graph(
                checkpointer=saver,
                extractor=extractor,
            )

    else:
        yield build_graph(extractor=extractor)