import logging
import os

from campaign_ai.config import Settings, get_settings
from campaign_ai.modules.requirements.prompts import SYSTEM_PROMPT
from campaign_ai.schema.requirement import Extraction


logger = logging.getLogger(__name__)


class ExtractionError(RuntimeError):
    pass


def validate_grounding(
    extraction: Extraction,
    brief: str,
) -> Extraction:
    supported = set()

    for item in extraction.evidence:
        if item.quote not in brief:
            raise ValueError(
                "Evidence quote was not found in the brief"
            )

        supported.add(item.field)

    for name, value in extraction.requirements.model_dump().items():
        if value not in (None, [], "") and name not in supported:
            raise ValueError(f"Missing evidence for {name}")

    for conflict in extraction.contradictions:
        invalid_quote = any(
            not quote.strip() or quote not in brief
            for quote in conflict.quotes
        )

        if invalid_quote:
            raise ValueError(
                "Contradiction evidence was not found in the brief"
            )

    return extraction


def extract_structured(
    brief: str,
    settings: Settings | None = None,
) -> Extraction:
    settings = settings or get_settings()

    # Avoid a metadata download when LiteLLM is imported.
    os.environ.setdefault(
        "LITELLM_LOCAL_MODEL_COST_MAP",
        "True",
    )

    import instructor
    import litellm

    client = instructor.from_litellm(
        litellm.completion,
        mode=instructor.Mode.JSON,
    )

    models = list(
        dict.fromkeys([
            settings.model,
            *settings.fallback_models,
        ])
    )

    provider_keys = {
        "openai": settings.openai_api_key,
        "anthropic": settings.anthropic_api_key,
        "gemini": settings.gemini_api_key,
        
        "openrouter": settings.openrouter_api_key,
   
    }

    for model in models:
        prefix = model.split("/", 1)[0]
        secret = provider_keys.get(prefix)

        kwargs = {}

        if secret and secret.get_secret_value():
            kwargs["api_key"] = secret.get_secret_value()

        for attempt in range(settings.llm_attempts):
            try:
                result = client.chat.completions.create(
                    model=model,
                    response_model=Extraction,
                    messages=[
                        {
                            "role": "system",
                            "content": SYSTEM_PROMPT,
                        },
                        {
                            "role": "user",
                            "content": brief,
                        },
                    ],
                    max_retries=1,
                    num_retries=0,
                    timeout=settings.llm_timeout_seconds,
                    **kwargs,
                )

                return validate_grounding(result, brief)

            except Exception as exc:
                # Do not log provider response bodies or credentials.
                logger.warning(
                    "Extraction attempt %s failed (%s)",
                    attempt + 1,
                    type(exc).__name__,
                )

    raise ExtractionError(
        "Extraction failed for all configured models. "
        "Check provider credentials and model settings."
    )