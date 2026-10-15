
import os

from dotenv import load_dotenv
from openai import OpenAI


load_dotenv()
#for on this too as its giving the rate limiting error

class GroqClient:
    def __init__(self):
        api_key = os.getenv("GROQ_API_KEY")
        model = os.getenv("GROQ_MODEL")

        if not api_key:
            raise ValueError("GROQ_API_KEY is not configured.")

        if not model:
            raise ValueError("GROQ_MODEL is not configured.")

        self.model = model
        self.client = OpenAI(
            api_key=api_key,
            base_url="https://api.groq.com/openai/v1",
            timeout=30.0,
            max_retries=2,
        )

    
    def generate(self, prompt: str) -> str:
        if not prompt.strip():
            raise ValueError("Prompt cannot be empty.")

        response = self.client.chat.completions.create(
            model=self.model,
            max_tokens=6000,
            response_format={"type": "json_object"},
            messages=[
                {
                    "role": "user",
                    "content": prompt,
                }
            ],
        )

        choice = response.choices[0]
        content = choice.message.content

        if choice.finish_reason == "length":
            raise RuntimeError(
                "Groq truncated its response at the output-token limit."
            )

        if not content or not content.strip():
            raise RuntimeError(
                f"Groq returned an empty response. "
                f"Finish reason: {choice.finish_reason}"
            )

        return content.strip()

