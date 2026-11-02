from contextlib import asynccontextmanager
from threading import RLock
from uuid import uuid4

from fastapi import FastAPI, HTTPException, Request
from langgraph.types import Command
from pydantic import Field, ValidationError

from campaign_ai.config import get_settings
from campaign_ai.graph.builder import graph_context
from campaign_ai.llm.gateway import ExtractionError
from campaign_ai.modules.requirements.service import (
    ApprovalBlocked,
    apply_operator_edits,
    clean_brief,
)
from campaign_ai.schema.requirement import (
    RequirementsResult,
    Review,
    StrictModel,
)


class StartRun(StrictModel):
    brief: str

    agency_id: str = Field(
        min_length=1,
        max_length=100,
        pattern=r"^[A-Za-z0-9_-]+$",
    )

    client_brand_id: str = Field(
        min_length=1,
        max_length=100,
        pattern=r"^[A-Za-z0-9_-]+$",
    )


class ConfirmRun(Review):
    revision: int = Field(ge=1)


class RunResponse(StrictModel):
    run_id: str
    agency_id: str
    client_brand_id: str

    revision: int
    paused: bool

    result: RequirementsResult


def create_app(extractor=None):
    @asynccontextmanager
    async def lifespan(app):
        with graph_context(
            extractor=extractor
        ) as graph:
            app.state.graph = graph
            app.state.lock = RLock()

            yield

    app = FastAPI(
        title="Campaign AI — Module 1",
        lifespan=lifespan,
    )

    @app.get("/health")
    def health():
        return {
            "status": "ok",
            "mode": (
                "fixture"
                if get_settings().demo_mode
                else "live"
            ),
        }

    def config(run_id):
        return {
            "configurable": {
                "thread_id": run_id,
            }
        }

    def snapshot(
        request,
        run_id,
        agency_id,
        client_brand_id,
    ):
        state = request.app.state.graph.get_state(
            config(run_id)
        )

        wrong_scope = (
            not state.values
            or state.values.get("agency_id") != agency_id
            or state.values.get("client_brand_id") != client_brand_id
        )

        if wrong_scope:
            raise HTTPException(
                status_code=404,
                detail="Run not found",
            )

        return state

    def response(run_id, state):
        values = state.values

        return RunResponse(
            run_id=run_id,
            agency_id=values["agency_id"],
            client_brand_id=values["client_brand_id"],
            revision=values["revision"],
            paused=bool(state.next),
            result=values["result"],
        )

    @app.post(
        "/runs",
        response_model=RunResponse,
        status_code=201,
    )
    def start_run(
        body: StartRun,
        request: Request,
    ):
        try:
            brief = clean_brief(body.brief)
            run_id = str(uuid4())

            request.app.state.graph.invoke(
                {
                    "brief": brief,
                    "agency_id": body.agency_id,
                    "client_brand_id": body.client_brand_id,
                },
                config(run_id),
            )

            state = request.app.state.graph.get_state(
                config(run_id)
            )

            return response(run_id, state)

        except ExtractionError as exc:
            raise HTTPException(
                status_code=502,
                detail=str(exc),
            ) from exc

        except ValueError as exc:
            raise HTTPException(
                status_code=422,
                detail=str(exc),
            ) from exc

    @app.get(
        "/runs/{run_id}",
        response_model=RunResponse,
    )
    def get_run(
        run_id: str,
        request: Request,
        agency_id: str,
        client_brand_id: str,
    ):
        state = snapshot(
            request,
            run_id,
            agency_id,
            client_brand_id,
        )

        return response(run_id, state)

    @app.post(
        "/runs/{run_id}/confirm",
        response_model=RunResponse,
    )
    def confirm_run(
        run_id: str,
        body: ConfirmRun,
        request: Request,
        agency_id: str,
        client_brand_id: str,
    ):
        # This lock protects one local API process.
        with request.app.state.lock:
            state = snapshot(
                request,
                run_id,
                agency_id,
                client_brand_id,
            )

            if not state.next:
                raise HTTPException(
                    status_code=409,
                    detail="This run is already finished",
                )

            if body.revision != state.values["revision"]:
                raise HTTPException(
                    status_code=409,
                    detail=(
                        "Review is stale; reload the run "
                        "before saving"
                    ),
                )

            review = Review.model_validate(
                body.model_dump(exclude={"revision"})
            )

            try:
                # Reject invalid approval before consuming
                # the saved graph interrupt.
                apply_operator_edits(
                    RequirementsResult.model_validate(
                        state.values["result"]
                    ),
                    review,
                )

                request.app.state.graph.invoke(
                    Command(
                        resume=review.model_dump(
                            mode="json"
                        )
                    ),
                    config(run_id),
                )

            except ApprovalBlocked as exc:
                raise HTTPException(
                    status_code=409,
                    detail=str(exc),
                ) from exc

            except (ValidationError, ValueError) as exc:
                raise HTTPException(
                    status_code=422,
                    detail=str(exc),
                ) from exc

            updated_state = (
                request.app.state.graph.get_state(
                    config(run_id)
                )
            )

            return response(run_id, updated_state)

    return app


app = create_app()