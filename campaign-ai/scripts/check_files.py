from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]

EXPECTED = [
    "pyproject.toml",
    ".python-version",
    ".env",

    "src/campaign_ai/config.py",
    "src/campaign_ai/samples.py",

    "src/campaign_ai/schemas/requirements.py",
    "src/campaign_ai/llm/gateway.py",

    "src/campaign_ai/modules/requirements/prompts.py",
    "src/campaign_ai/modules/requirements/extract.py",
    "src/campaign_ai/modules/requirements/validate.py",
    "src/campaign_ai/modules/requirements/service.py",

    "src/campaign_ai/graph/state.py",
    "src/campaign_ai/graph/nodes.py",
    "src/campaign_ai/graph/builder.py",

    "src/campaign_ai/api/main.py",

    "scripts/run_local.py",
    "demo/streamlit_app.py",

    "tests/test_validation.py",
    "tests/test_service.py",
    "tests/test_workflow.py",
    "tests/test_gateway.py",
]

PACKAGE_FOLDERS = [
    "",
    "schemas/",
    "llm/",
    "modules/",
    "modules/requirements/",
    "graph/",
    "api/",
]

EXPECTED += [
    f"src/campaign_ai/{folder}__init__.py"
    for folder in PACKAGE_FOLDERS
]

missing = [
    name
    for name in EXPECTED
    if not (ROOT / name).is_file()
]

if missing:
    print("Missing files:")

    for name in missing:
        print(name)

else:
    print(
        f"All {len(EXPECTED)} required files are present."
    )

raise SystemExit(bool(missing))