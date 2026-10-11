import os
import base64
import requests


def analyze_design(image_path, requirements, recommendation):

    with open(image_path, "rb") as image_file:
        image_data = base64.b64encode(
            image_file.read()
        ).decode("utf-8")

    prompt = f"""
Analyze this design according to these campaign requirements:

Product: {requirements["product"]}
Age range: {requirements["age_range"]}
Market: {requirements["market"]}
Brand positioning: {requirements["brand_positioning"]}
Campaign type: {requirements["campaign_type"]}
Platforms: {requirements["platforms"]}

Design direction:
{recommendation["design_direction"]}

Evaluate:
1. Whether the design matches the requirements
2. Colors
3. Layout
4. Typography
5. Target audience suitability
6. Three specific improvements
"""

    response = requests.post(
        "https://openrouter.ai/api/v1/chat/completions",
        headers={
            "Authorization": f"Bearer {os.environ['OPENROUTER_API_KEY']}",
            "Content-Type": "application/json"
        },
        json={
            "model": "inclusionai/ling-3.0-flash-vl:free",
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": prompt
                        },
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/png;base64,{image_data}"
                            }
                        }
                    ]
                }
            ]
        }
    )

    response.raise_for_status()

    result = response.json()

    return result["choices"][0]["message"]["content"]