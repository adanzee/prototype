from campaign_ai.config import get_settings
from campaign_ai.llm.gateway import extract_structured


def extract_requirements(brief: str):
    if get_settings().demo_mode:
        from campaign_ai.samples import fixture_extract

        return fixture_extract(brief)

    return extract_structured(brief)