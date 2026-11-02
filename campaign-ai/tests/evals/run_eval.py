import json
from pathlib import Path

from campaign_ai.modules.requirements.service import understand_brief


def jaccard(a: set, b: set) -> float:
    return 1.0 if not a and not b else len(a & b) / len(a | b)


def score(req, expected: dict) -> dict:
    scores = {}
    if "objective" in expected:
        got = req.objective.value if req.objective else None
        scores["objective"] = float(got == expected["objective"])
    if "channels" in expected:
        scores["channels"] = jaccard({c.value for c in req.channels}, set(expected["channels"]))
    if "regions" in expected:
        scores["regions"] = jaccard({r.lower() for r in req.regions}, set(expected["regions"]))
    if "product_or_service" in expected:
        got = (req.product_or_service or "").lower()
        scores["product_or_service"] = float(expected["product_or_service"] in got)
    return scores


def main():
    totals: dict[str, list[float]] = {}
    for path in sorted(Path(__file__).parent.glob("briefs/*.json")):
        case = json.loads(path.read_text())
        req = understand_brief(case["brief"]).requirements
        for field, value in score(req, case["expected"]).items():
            totals.setdefault(field, []).append(value)
        print(path.name, "done")

    print("\nField accuracy:")
    for field, values in totals.items():
        print(f"  {field:22s} {sum(values) / len(values):.2f}  (n={len(values)})")


if __name__ == "__main__":
    main()