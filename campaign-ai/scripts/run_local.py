import argparse
import json
from pathlib import Path
from uuid import uuid4

from langgraph.types import Command

from campaign_ai.graph.builder import graph_context
from campaign_ai.modules.requirements.service import (
    apply_operator_edits,
)
from campaign_ai.samples import SAMPLES, fixture_extract
from campaign_ai.schema.requirement import (
    RequirementsResult,
    Review,
)


def main():
    parser = argparse.ArgumentParser(
        description="Extract and review a campaign brief"
    )

    parser.add_argument(
        "--demo",
        action="store_true",
        help="Use Sample 1 without an API key",
    )

    parser.add_argument(
        "--brief-file",
        type=Path,
    )

    parser.add_argument(
        "--smoke",
        action="store_true",
        help="With --demo, automatically add UAE and approve",
    )

    args = parser.parse_args()

    if args.smoke and not args.demo:
        parser.error("--smoke requires --demo")

    if not args.demo and not args.brief_file:
        parser.error("Supply --brief-file or --demo")

    brief = (
        next(iter(SAMPLES.values()))
        if args.demo
        else args.brief_file.read_text()
    )

    config = {
        "configurable": {
            "thread_id": str(uuid4()),
        }
    }

    with graph_context(
        extractor=fixture_extract if args.demo else None
    ) as graph:
        graph.invoke(
            {
                "brief": brief,
                "agency_id": "local",
                "client_brand_id": "demo",
            },
            config,
        )

        while True:
            state = graph.get_state(config)

            print(
                json.dumps(
                    state.values["result"],
                    indent=2,
                )
            )

            if not state.next:
                print(
                    "APPROVED — ready for the next module"
                )
                return

            print("PAUSED — human review is required")

            if args.smoke:
                review_data = {
                    "edits": {
                        "regions": ["UAE"],
                    },
                    "approve": True,
                }

            else:
                try:
                    review_data = json.loads(
                        input(
                            "Review JSON "
                            "(edits, resolutions, approve): "
                        )
                    )

                except json.JSONDecodeError as exc:
                    print(f"Invalid JSON: {exc}")
                    continue

            try:
                review = Review.model_validate(
                    review_data
                )

                apply_operator_edits(
                    RequirementsResult.model_validate(
                        state.values["result"]
                    ),
                    review,
                )

                graph.invoke(
                    Command(
                        resume=review.model_dump(
                            mode="json"
                        )
                    ),
                    config,
                )

            except ValueError as exc:
                print(f"Review rejected: {exc}")


if __name__ == "__main__":
    main()