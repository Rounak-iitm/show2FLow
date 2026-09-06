from show2flow.core.recorder import load_workflow, save_workflow
from show2flow.core.workflow import Workflow, WorkflowStep


def test_workflow_schema_roundtrip(tmp_path):
    wf = Workflow(
        name="unit_test_wf",
        description="test",
        steps=[
            WorkflowStep(id="s1", tool="files", action="save_json", args={"path": "x.json", "data": []}),
        ],
    )
    out_path = tmp_path / "wf.yaml"
    save_workflow(wf, out_path)
    loaded = load_workflow(out_path)
    assert loaded.name == "unit_test_wf"
    assert loaded.step_by_id("s1").tool == "files"


def test_example_workflow_loads():
    wf = load_workflow("search_jobs.yaml")
    assert wf.name == "search_jobs"
    assert len(wf.steps) == 5
    assert wf.steps[0].tool == "browser"
