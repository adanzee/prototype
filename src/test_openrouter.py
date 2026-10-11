import os
import base64
from openai import OpenAI


client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=os.environ["OPENROUTER_API_KEY"]
)


with open("/home/devel/prototype/design_intelligence/test_file/test.png", "rb") as image_file:
    image_data = base64.b64encode(image_file.read()).decode("utf-8")


response = client.chat.completions.create(
    model="inclusionai/ling-3.0-flash-vl:free",
    messages=[
        {
            "role": "user",
            "content": [
                {
                    "type": "text",
                    "text": (
                        "Analyze this image. Describe the design, "
                        "colors, layout, and give 3 suggestions "
                        "for improvement."
                    )
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
)


print(response.choices[0].message.content)