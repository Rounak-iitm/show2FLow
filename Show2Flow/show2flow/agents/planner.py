
from __future__ import annotations

from show2flow.agents.intent import Intent
from show2flow.core.workflow import Workflow, WorkflowStep


def plan(intent: Intent, workflow_name: str = "generated_workflow") -> Workflow:
    if intent.action != "search_and_extract":
        raise ValueError(f"Planner has no template for intent action '{intent.action}'")
    if not intent.url:
        raise ValueError("search_and_extract intent requires a URL")
    if not intent.query:
        raise ValueError("search_and_extract intent requires a query")

    save_path = intent.save_path or "runs/output.json"

    steps = [
        WorkflowStep(
            id="open_site",
            tool="browser",
            action="open",
            args={"url": intent.url},
            target_description="the site's homepage",
        ),
        WorkflowStep(
            id="fill_search",
            tool="browser",
            action="fill",
            args={"selector": "input[type=search], input[name=q], input[type=text]", "text": intent.query},
            target_description="the main search input box",
        ),
        WorkflowStep(
            id="submit_search",
            tool="browser",
            action="press",
            args={"selector": "input[type=search], input[name=q], input[type=text]", "key": "Enter"},
            target_description="submit the search",
        ),
        WorkflowStep(
            id="extract_results",
            tool="browser",
            action="extract",
            args={"selector": "h2, h3, .result-title", "limit": intent.result_limit},
            target_description="the titles of the search result items",
            expect={"type": "list", "min_items": 1},
        ),
        WorkflowStep(
            id="save_results",
            tool="files",
            action="save_json",
            args={"path": save_path, "data": "$extract_results"},
            target_description="persist the extracted results to disk",
        ),
    ]
    return Workflow(name=workflow_name, description=intent.raw_text, steps=steps)
