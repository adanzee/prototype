from web_search import search_campaigns


requirements = {
    "product": "perfume",
    "age_range": "17-30",
    "market": "Middle East",
    "brand_positioning": "elite",
    "campaign_type": "a social media campaign",
    "platforms": "all platforms"
}


results = search_campaigns(requirements)

for result in results:
    print(result["title"])
    print(result["url"])
    print(result.get("content", result.get("snippet", "")))
    print("-" * 50)