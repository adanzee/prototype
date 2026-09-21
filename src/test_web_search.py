from web_search import search_campaigns


requirements = {
    "product": "perfume",
    "age_range": "17-30",
    "market": "Middle East",
    "brand_positioning": "elite",
    "campaign_type": "a social media campaign",
    "platforms": "all platforms"
}


campaigns = search_campaigns(requirements)

for campaign in campaigns:
    print("TITLE:", campaign["title"])
    print("URL:", campaign["url"])
    print("CONTENT:", campaign["content"][:500])
    print("=" * 60)