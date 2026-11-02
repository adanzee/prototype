from types import SimpleNamespace

import pytest

from campaign_ai.config import Settings
from campaign_ai.llm.gateway import (
    ExtractionError,
    extract_structured,
)
from campaign_ai.samples import SAMPLES, fixture_extract


def test_gateway_retries_invalid_output_then_falls_back(
    monkeypatch,
):
    import instructor

    calls = []

    good = fixture_extract(
        next(iter(SAMPLES.values()))
    )

    def create(**kwargs):
        calls.append(kwargs["model"])

        if kwargs["model"] == "openai/broken":
            bad = good.model_copy(deep=True)

            bad.evidence[0].quote = (
                "invented quote"
            )

            return bad

        return good

    client = SimpleNamespace(
        chat=SimpleNamespace(
            completions=SimpleNamespace(
                create=create,
            )
        )
    )

    monkeypatch.setattr(
        instructor,
        "from_litellm",
        lambda *args, **kwargs: client,
    )

    settings = Settings(
        _env_file=None,
        model="openai/broken",
        fallback_models=["openai/working"],
        llm_attempts=2,
    )

    result = extract_structured(
        next(iter(SAMPLES.values())),
        settings,
    )

    assert result == good

    assert calls == [
        "openai/broken",
        "openai/broken",
        "openai/working",
    ]


def test_gateway_failure_is_sanitized(monkeypatch):
    import instructor

    def fail(**kwargs):
        raise RuntimeError(
            "private provider data"
        )

    client = SimpleNamespace(
        chat=SimpleNamespace(
            completions=SimpleNamespace(
                create=fail,
            )
        )
    )

    monkeypatch.setattr(
        instructor,
        "from_litellm",
        lambda *args, **kwargs: client,
    )

    with pytest.raises(
        ExtractionError
    ) as error:
        extract_structured(
            "brief",
            Settings(
                _env_file=None,
                llm_attempts=1,
            ),
        )

    assert (
        "private provider data"
        not in str(error.value)
    )