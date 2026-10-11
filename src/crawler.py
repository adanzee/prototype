import requests
from bs4 import BeautifulSoup


def crawl_page(url):

    response = requests.get(
        url,
        timeout=10,
        headers={
            "User-Agent": "Mozilla/5.0"
        }
    )

    response.raise_for_status()

    soup = BeautifulSoup(response.text, "html.parser")

    for element in soup(["script", "style", "nav", "footer"]):
        element.decompose()

    text = soup.get_text(separator=" ", strip=True)

    return text