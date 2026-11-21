import json
from datetime import date
from urllib.parse import urlencode
from urllib.request import urlopen


EUROPE_PMC_SEARCH = "https://www.ebi.ac.uk/europepmc/webservices/rest/search"


def discover_papers(query: str, limit: int = 5) -> list[dict]:
    query = query.strip()
    if not query:
        raise ValueError("Enter a research query.")
    if not 1 <= limit <= 50:
        raise ValueError("Limit must be between 1 and 50.")

    params = urlencode({
        "query": f"({query}) AND OPEN_ACCESS:Y",
        "format": "json",
        "resultType": "core",
        "pageSize": limit,
    })

    with urlopen(f"{EUROPE_PMC_SEARCH}?{params}", timeout=20) as response:
        payload = json.load(response)

    candidates = []
    for paper in payload["resultList"]["result"]:
        if not (paper.get("source") and paper.get("id") and paper.get("title")):
            continue

        candidates.append({
            "url": f"https://europepmc.org/article/{paper['source']}/{paper['id']}",
            "title": paper["title"],
            "kind": "study",
            "collected_on": date.today().isoformat(),
            "published_on": paper.get("firstPublicationDate"),
            "doi": paper.get("doi"),
        })

    return candidates