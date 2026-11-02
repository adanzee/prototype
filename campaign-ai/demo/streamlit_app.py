import json
import os

import httpx
import streamlit as st

from campaign_ai.samples import SAMPLES


st.set_page_config(
    page_title="Campaign brief review",
    page_icon="📝",
    layout="wide",
)

st.title("Campaign brief review")

st.caption(
    "Module 1 · Extract → validate → human review → approve"
)

api_url = st.sidebar.text_input(
    "API URL",
    os.getenv(
        "API_URL",
        "http://127.0.0.1:8000",
    ),
).rstrip("/")

agency = st.sidebar.text_input(
    "Agency ID",
    "demo-agency",
)

brand = st.sidebar.text_input(
    "Client brand ID",
    "luma",
)

scope = {
    "agency_id": agency,
    "client_brand_id": brand,
}

context = (
    api_url,
    agency,
    brand,
)

if st.session_state.get("context") != context:
    st.session_state.pop("run", None)
    st.session_state.context = context


def api(method, path, **kwargs):
    try:
        response = httpx.request(
            method,
            api_url + path,
            timeout=180,
            trust_env=False,
            **kwargs,
        )

        if response.is_error:
            detail = response.json().get(
                "detail",
                "Request failed",
            )

            st.error(
                f"API {response.status_code}: {detail}"
            )

            return None

        return response.json()

    except (httpx.HTTPError, ValueError):
        st.error(
            "Cannot reach the API or read its response. "
            "Check the URL and start Uvicorn."
        )

        return None


if st.sidebar.button("Check API connection"):
    health = api("GET", "/health")

    if health:
        st.sidebar.success(
            f"Connected · {health['mode']} mode"
        )

        if health["mode"] == "fixture":
            st.info(
                "Fixture mode uses precomputed answers "
                "for the three sample briefs only."
            )


sample = st.selectbox(
    "Sample brief",
    list(SAMPLES),
)

if st.button("Load sample"):
    st.session_state.brief = SAMPLES[sample]

st.text_area(
    "Campaign brief",
    key="brief",
    height=180,
)

if st.button("Analyze", type="primary"):
    with st.spinner("Analyzing brief…"):
        run = api(
            "POST",
            "/runs",
            json={
                "brief": st.session_state.brief,
                **scope,
            },
        )

    if run:
        st.session_state.run = run
        st.rerun()


run = st.session_state.get("run")

if run:
    if st.button("Reload saved run"):
        latest = api(
            "GET",
            f"/runs/{run['run_id']}",
            params=scope,
        )

        if latest:
            st.session_state.run = latest
            st.rerun()

    result = run["result"]

    st.caption(
        f"Run {run['run_id']} · "
        f"revision {run['revision']}"
    )

    if result["status"] == "approved":
        st.success(
            "Approved — the clean requirements record "
            "is ready for the next module."
        )

        st.json(result["requirements"])

        st.download_button(
            "Download approved record",
            json.dumps(run, indent=2),
            "approved-requirements.json",
            "application/json",
        )

    else:
        left, right = st.columns([2, 1])

        with right:
            st.subheader("Review questions")

            for question in result["questions"]:
                label = (
                    "Required"
                    if question["blocking"]
                    else "Recommended"
                )

                st.write(
                    f"**{label}:** {question['text']}"
                )

            with st.expander(
                "Original extraction evidence"
            ):
                st.json(result["evidence"])

        with left:
            form_key = (
                f"review-{run['run_id']}-"
                f"{run['revision']}"
            )

            with st.form(form_key):
                st.subheader("Edit requirements")

                edits = {}

                for field, value in (
                    result["requirements"].items()
                ):
                    label = (
                        field.replace("_", " ").title()
                    )

                    if isinstance(value, list):
                        text = st.text_area(
                            label + " (one per line)",
                            "\n".join(value),
                            height=68,
                        )

                        edits[field] = [
                            line.strip()
                            for line in text.splitlines()
                            if line.strip()
                        ]

                    else:
                        if field.endswith("_date"):
                            label += " (YYYY-MM-DD)"

                        text = st.text_input(
                            label,
                            value or "",
                        )

                        edits[field] = (
                            text.strip() or None
                        )

                resolutions = {}

                for index, conflict in enumerate(
                    result["contradictions"]
                ):
                    key = f"conflict:{index}"

                    st.write(
                        conflict["description"]
                    )

                    st.caption(
                        " | ".join(conflict["quotes"])
                    )

                    note = st.text_input(
                        "Resolution explanation",
                        result["resolutions"].get(
                            key,
                            "",
                        ),
                        key=key + str(
                            run["revision"]
                        ),
                    )

                    if note.strip():
                        resolutions[key] = (
                            note.strip()
                        )

                save = st.form_submit_button(
                    "Save changes"
                )

                approve = st.form_submit_button(
                    "Approve",
                    type="primary",
                )

            if save or approve:
                updated = api(
                    "POST",
                    f"/runs/{run['run_id']}/confirm",
                    params=scope,
                    json={
                        "revision": run["revision"],
                        "edits": edits,
                        "resolutions": resolutions,
                        "approve": approve,
                    },
                )

                if updated:
                    st.session_state.run = updated
                    st.rerun()