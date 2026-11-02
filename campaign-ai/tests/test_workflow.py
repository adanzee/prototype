from uuid import uuid4

from fastapi.testclient import TestClient
from langgraph.types import Command

from campaign_ai.api.main import create_app
from campaign_ai.graph.builder import build_graph
from campaign_ai.samples import SAMPLES, fixture_extract


SCOPE = {
    "agency_id": "agency",
    "client_brand_id": "brand",
}


def test_pause_repeated_edits_and_finish_without_reextraction():
    calls = []

    def extract(brief):
        calls.append(brief)
        return fixture_extract(brief)

    graph = build_graph(extractor=extract)

    config = {
        "configurable": {
            "thread_id": str(uuid4()),
        }
    }

    graph.invoke(
        {
            "brief": list(SAMPLES.values())[0],
            **SCOPE,
        },
        config,
    )

    assert graph.get_state(config).next == (
        "confirm",
    )

    graph.invoke(
        Command(
            resume={
                "edits": {
                    "regions": ["UAE"],
                }
            }
        ),
        config,
    )

    assert graph.get_state(config).next == (
        "confirm",
    )

    graph.invoke(
        Command(
            resume={"approve": True}
        ),
        config,
    )

    state = graph.get_state(config)

    assert not state.next

    assert (
        state.values["result"]["status"]
        == "approved"
    )

    assert len(calls) == 1


def test_api_walkthrough_and_rejected_approval_preserves_pause():
    with TestClient(
        create_app(fixture_extract)
    ) as client:
        assert client.get(
            "/docs"
        ).status_code == 200

        assert client.get(
            "/openapi.json"
        ).status_code == 200

        assert client.get(
            "/health"
        ).json()["status"] == "ok"

        response = client.post(
            "/runs",
            json={
                "brief": list(SAMPLES.values())[0],
                **SCOPE,
            },
        )

        assert response.status_code == 201, response.text

        run = response.json()
        path = f"/runs/{run['run_id']}"

        rejected = client.post(
            path + "/confirm",
            params=SCOPE,
            json={
                "revision": 1,
                "approve": True,
            },
        )

        assert rejected.status_code == 409

        current = client.get(
            path,
            params=SCOPE,
        ).json()

        assert current["revision"] == 1
        assert current["paused"]

        saved = client.post(
            path + "/confirm",
            params=SCOPE,
            json={
                "revision": 1,
                "edits": {
                    "regions": ["UAE"],
                },
            },
        )

        assert saved.status_code == 200, saved.text
        assert saved.json()["paused"]
        assert saved.json()["revision"] == 2

        stale = client.post(
            path + "/confirm",
            params=SCOPE,
            json={
                "revision": 1,
                "approve": True,
            },
        )

        assert stale.status_code == 409

        approved = client.post(
            path + "/confirm",
            params=SCOPE,
            json={
                "revision": 2,
                "approve": True,
            },
        )

        assert approved.status_code == 200, approved.text

        assert (
            approved.json()["result"]["status"]
            == "approved"
        )

        assert not approved.json()["paused"]

        finished = client.post(
            path + "/confirm",
            params=SCOPE,
            json={
                "revision": 3,
                "approve": True,
            },
        )

        assert finished.status_code == 409

        wrong_agency = client.get(
            path,
            params={
                **SCOPE,
                "agency_id": "other",
            },
        )

        assert wrong_agency.status_code == 404

        wrong_brand = client.get(
            path,
            params={
                **SCOPE,
                "client_brand_id": "other",
            },
        )

        assert wrong_brand.status_code == 404

        assert client.get(
            "/runs/unknown",
            params=SCOPE,
        ).status_code == 404


def test_api_conflict_and_input_validation():
    with TestClient(
        create_app(fixture_extract)
    ) as client:
        empty = client.post(
            "/runs",
            json={
                "brief": " ",
                **SCOPE,
            },
        )

        assert empty.status_code == 422

        run = client.post(
            "/runs",
            json={
                "brief": list(SAMPLES.values())[2],
                **SCOPE,
            },
        ).json()

        path = (
            f"/runs/{run['run_id']}/confirm"
        )

        blocked = client.post(
            path,
            params=SCOPE,
            json={
                "revision": 1,
                "approve": True,
            },
        )

        assert blocked.status_code == 409

        invalid = client.post(
            path,
            params=SCOPE,
            json={
                "revision": 1,
                "edits": {
                    "regions": "UAE",
                },
            },
        )

        assert invalid.status_code == 422

        approved = client.post(
            path,
            params=SCOPE,
            json={
                "revision": 1,
                "edits": {
                    "tone": ["formal"],
                },
                "resolutions": {
                    "conflict:0": (
                        "Client confirmed formal."
                    ),
                },
                "approve": True,
            },
        )

        assert approved.status_code == 200, approved.text

        assert (
            approved.json()["result"]["status"]
            == "approved"
        )