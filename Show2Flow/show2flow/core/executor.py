
from __future__ import annotations

import time
from typing import Any, Dict

from show2flow.agents import healer, verifier
from show2flow.core.recorder import new_run_id, save_run
from show2flow.core.state import RunState, StepResult
from show2flow.core.workflow import Workflow
from show2flow.tools.registry import ToolRegistry, default_registry


class ExecutionError(Exception):
    pass


def _resolve_args(args: Dict[str, Any], outputs: Dict[str, Any]) -> Dict[str, Any]:
    """Replace any string arg value of the form "$step_id" with that
    step's recorded output."""
    resolved = {}
    for k, v in args.items():
        if isinstance(v, str) and v.startswith("$") and v[1:] in outputs:
            resolved[k] = outputs[v[1:]]
        else:
            resolved[k] = v
    return resolved


def run_workflow(
    workflow: Workflow,
    registry: ToolRegistry | None = None,
    enable_healing: bool = True,
    persist: bool = True,
) -> RunState:
    registry = registry or default_registry()
    state = RunState(workflow_name=workflow.name, run_id=new_run_id())
    outputs: Dict[str, Any] = {}

    print(f"[Show2Flow] Task received: {workflow.description or workflow.name}")

    for step in workflow.steps:
        started = time.time()
        args = _resolve_args(step.args, outputs)
        status = "success"
        output = None
        error = None
        healed_from = healed_to = None
        confidence = None

        try:
            fn = registry.resolve_action(step.tool, step.action)
            output = fn(**args)
            ok, reason = verifier.verify(output, step.expect)
            if not ok:
                raise ExecutionError(reason)
            print(f"[{step.tool.capitalize()}] {step.id}: ok")

        except Exception as exc:  # noqa: BLE001 - deliberately broad, healed or reported
            if enable_healing and step.tool == "browser" and step.target_description:
                print(f"[Executor] Step '{step.id}' failed: {exc}")
                print("[Healer] Searching semantic alternatives...")
                browser_tool = registry.get("browser")
                heal_result = healer.heal(browser_tool, step.target_description)

                if heal_result.matched:
                    print(
                        f"[Healer] Candidate: {heal_result.matched_text!r} "
                        f"(confidence: {heal_result.confidence})"
                    )
                    healed_from = dict(args)
                    selector_key = "selector" if "selector" in args else None
                    healed_args = dict(args)
                    if selector_key:
                        healed_args[selector_key] = heal_result.selector
                    try:
                        fn = registry.resolve_action(step.tool, step.action)
                        output = fn(**healed_args)
                        ok, reason = verifier.verify(output, step.expect)
                        if not ok:
                            raise ExecutionError(reason)
                        status = "healed"
                        healed_to = healed_args
                        confidence = heal_result.confidence
                        print("[Verifier] Action successful")
                        print("[Healer] Workflow repaired")
                    except Exception as exc2:  # noqa: BLE001
                        status = "failed"
                        error = f"original error: {exc}; heal attempt error: {exc2}"
                else:
                    status = "failed"
                    error = f"{exc} (no confident semantic match found)"
            else:
                status = "failed"
                error = str(exc)

        finished = time.time()
        result = StepResult(
            step_id=step.id,
            tool=step.tool,
            action=step.action,
            status=status,
            started_at=started,
            finished_at=finished,
            output=output,
            error=error,
            healed_from=healed_from,
            healed_to=healed_to,
            healer_confidence=confidence,
        )
        state.add(result)
        outputs[step.id] = output

        if status == "failed":
            print(f"[Executor] Step '{step.id}' failed permanently: {error}")
            break

    state.finish()

    browser_tool = registry._tools.get("browser") if hasattr(registry, "_tools") else None
    if browser_tool is not None:
        try:
            browser_tool.close()
        except Exception:  # noqa: BLE001
            pass

    if persist:
        path = save_run(state)
        print(f"[Recorder] Run saved to {path}")

    summary = state.summary()
    if summary["failed"] == 0:
        print("\nWorkflow completed successfully.")
    else:
        print(f"\nWorkflow finished with {summary['failed']} failed step(s).")

    return state
