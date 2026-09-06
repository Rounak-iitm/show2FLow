"""Show2Flow command-line interface.

Usage:
    python -m show2flow.cli run workflows/examples/search_jobs.yaml
    python -m show2flow.cli plan "Open example.com and search for AI jobs, extract the first 5 results"
    python -m show2flow.cli list-runs
"""
from __future__ import annotations

import argparse
import json
import sys

from show2flow.agents import intent, planner
from show2flow.core.executor import run_workflow
from show2flow.core.recorder import list_runs, load_workflow, save_workflow


def cmd_run(args: argparse.Namespace) -> None:
    workflow = load_workflow(args.workflow_path)
    run_workflow(workflow, enable_healing=not args.no_heal)


def cmd_plan(args: argparse.Namespace) -> None:
    parsed_intent = intent.parse(args.task_text, default_url=args.url)
    workflow = planner.plan(parsed_intent, workflow_name=args.name)
    path = save_workflow(workflow)
    print(f"[Planner] {len(workflow.steps)} steps generated -> {path}")
    if args.run:
        run_workflow(workflow, enable_healing=not args.no_heal)


def cmd_list_runs(_args: argparse.Namespace) -> None:
    runs = list_runs()
    if not runs:
        print("No runs recorded yet.")
        return
    for r in runs:
        data = json.loads(r.read_text())
        print(
            f"{r.name:45s} success={data['success']} healed={data['healed']} "
            f"failed={data['failed']} ({data['duration_seconds']}s)"
        )


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="show2flow")
    sub = p.add_subparsers(dest="command", required=True)

    p_run = sub.add_parser("run", help="Run a workflow YAML file")
    p_run.add_argument("workflow_path")
    p_run.add_argument("--no-heal", action="store_true", help="Disable self-healing")
    p_run.set_defaults(func=cmd_run)

    p_plan = sub.add_parser("plan", help="Turn a natural-language task into a workflow")
    p_plan.add_argument("task_text")
    p_plan.add_argument("--url", default=None, help="Default URL if the task text has none")
    p_plan.add_argument("--name", default="generated_workflow")
    p_plan.add_argument("--run", action="store_true", help="Run the generated workflow immediately")
    p_plan.add_argument("--no-heal", action="store_true")
    p_plan.set_defaults(func=cmd_plan)

    p_list = sub.add_parser("list-runs", help="List recorded runs")
    p_list.set_defaults(func=cmd_list_runs)

    return p


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    sys.exit(main())
