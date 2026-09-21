import os
from tavily import TavilyClient


client = TavilyClient(
    api_key=os.environ["TAVILY_API_KEY"]
)


def search_campaigns(requirements):

    query = (
        f"{requirements['market']} "
        f"{requirements['product']} "
        f"{requirements['brand_positioning']} "
        f"{requirements['campaign_type']}"
    )

    response = client.search(
        query,
        max_results=5
    )

    return response["results"]