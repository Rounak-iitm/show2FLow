# Show2Flow

**An orchestration/automation layer that connects existing open-source AI
tools into semantic, self-healing workflows.**

Show2Flow is a backend/tool-engineering project (no frontend, no database —
`workflows/`, `recordings/`, `runs/`, and `experiments/` are the persistence
layer). It sits **above** tools like Playwright, Browser Use, Unstructured,
and Hugging Face models, and adds the part that isn't already open source:
a workflow engine with verification and **self-healing** when a target
application's UI changes.

```text
Human Task
    │
    ▼
Show2Flow
    │
    ├── Browser Tool        → Playwright / Browser Use
    ├── File Tool           → Python filesystem
    ├── Document Tool       → Unstructured (Phase 3)
    ├── AI Tool             → Hugging Face model
    ├── Tool Protocol       → MCP
    ├── Workflow Engine     → this repo
    └── Verification /      → this repo (the research contribution)
        Self-Healing
```

## Why this exists

Deterministic browser automation (fixed selectors/XPaths) breaks the moment
a page changes — a button renamed from "Search Jobs" to "Find Jobs" is
enough to fail a whole pipeline. Show2Flow's engine executes a step, and if
it fails, hands the step's plain-English `target_description` to a healer
that looks at every interactive element currently on the page and finds the
closest semantic match, then retries. This is also the project's research
question — see [Research](#research-component) below.

## Project structure

```text
show2flow/
├── core/
│   ├── workflow.py     # Workflow/WorkflowStep schema (pydantic)
│   ├── executor.py     # runs a workflow: verify -> heal -> retry loop
│   ├── recorder.py     # save/load workflows (YAML) and runs (JSON)
│   └── state.py        # RunState / StepResult
├── agents/
│   ├── intent.py        # natural language -> Intent (rule-based, swappable)
│   ├── planner.py        # Intent -> Workflow
│   ├── verifier.py       # did the step's output actually satisfy `expect`?
│   └── healer.py         # semantic repair: difflib, or embeddings if installed
├── tools/
│   ├── browser.py        # Playwright wrapper
│   ├── files.py          # save/read JSON & text
│   ├── documents.py       # PDF text extraction (pypdf); Unstructured later
│   └── registry.py        # tool name -> instance -> action lookup
├── mcp/
│   └── server.py          # exposes Show2Flow's tools over MCP
├── models/
│   └── provider.py         # model backend abstraction (Hugging Face)
└── cli.py                  # command-line entry point

workflows/examples/   # workflow YAML files
recordings/            # saved browser recordings (future)
runs/                   # JSON output of every executed run
experiments/             # Phase 6 benchmark results
tests/
configs/default.yaml
```

## Setup

```bash
# from the repo root
python -m venv C:\venvs\show2flow        # keep the venv OUTSIDE the repo path
C:\venvs\show2flow\Scripts\activate

pip install -r requirements.txt
playwright install chromium
```

> The README plan intentionally avoids a `.venv` nested inside a long path
> like `...\internship_IIIT_Agartala\Show2flow` — that caused environment
> issues in an earlier project. Point the venv somewhere short instead
> (`C:\venvs\show2flow`), and keep the source code where it already is.

## Running the demo

```bash
python -m show2flow.cli run workflows/examples/search_jobs.yaml
```

Expected output:

```text
[Show2Flow] Task received
[Browser] open_site: ok
[Browser] fill_search: ok
[Browser] submit_search: ok
[Browser] extract_results: ok
[Files] save_results: ok

Workflow completed successfully.
```

### The important demo: self-healing

Run `click_demo.yaml` against a page, then rename the button it looks for
(or point it at a page where the text has changed from "Search Jobs" to
"Find Jobs") and run again:

```bash
python -m show2flow.cli run workflows/examples/click_demo.yaml
```

```text
[Executor] Step 'click_search_button' failed: Timeout ...
[Healer] Searching semantic alternatives...
[Healer] Candidate: "Find Jobs" (confidence: 0.93)
[Verifier] Action successful
[Healer] Workflow repaired
```

Every run — healed or not — is saved as JSON under `runs/`, including the
original args, the healed args, and the healer's confidence, which is what
the Phase 6 experiments consume.

### Planning a workflow from natural language

```bash
python -m show2flow.cli plan "Open https://example.com and search for AI jobs, extract the first 5 results" --run
```

## Build phases

| Phase | Adds | Status |
|---|---|---|
| 1 | Python, Playwright, PyYAML, Pydantic, pytest — schema, recorder, executor, verifier | ✅ implemented |
| 2 | Hugging Face — intent parsing, semantic planning | scaffolded (`models/provider.py`, `agents/intent.py`) |
| 3 | MCP — Show2Flow tools exposed to other agents; Unstructured document pipeline | scaffolded (`mcp/server.py`, `tools/documents.py`) |
| 4 | Browser Use — only where it beats plain Playwright | not yet added |
| 5 | Self-healing engine | ✅ implemented (`agents/healer.py`, difflib backend; embedding backend auto-enables if `sentence-transformers` is installed) |
| 6 | Experiments + benchmark | not yet added — see below |

## Research component

**How effectively can semantic AI repair deterministic automation workflows
when application interfaces change?**

Planned comparison (`experiments/`):

```text
Static XPath  vs  CSS Selector  vs  Semantic Matching  vs  Show2Flow Self-Healing
```

Metrics to collect per run (`runs/*.json` already logs everything needed):
success rate, repair rate, execution latency, false repairs, healer
confidence, and number of model calls.

## Tests

```bash
pytest
```

7 unit tests currently cover the workflow schema round-trip, the intent
parser, the planner, the verifier, and the healer's difflib matching
backend (no browser required to run these).

## License

MIT (see LICENSE, or replace with whatever your internship requires).
