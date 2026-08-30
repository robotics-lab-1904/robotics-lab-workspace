# AI-Agent Workspace Structure

- Date: 2026-08-29
- Status: Completed
- Owner/agent: Codex

## Objective

Prepare the robotics lab workspace for effective collaboration with AI agents by adding concise automatic instructions and a structured, durable knowledge base for environment facts, task reports, decisions, runbooks, and handoffs.

## Success criteria

- A concise root `AGENTS.md` is automatically discoverable.
- Camera-specific constraints are layered through a nested `AGENTS.md`.
- Evolving task history is stored outside instruction files.
- New agents can identify the environment, project boundaries, current state, and relevant prior evidence.
- Reusable templates make future reports consistent.
- All new material is written in English and contains no secrets.

## Initial state

- No `AGENTS.md` or `AGENTS.override.md` was present in the workspace tree.
- Empty read-only `.agents/` and `.codex/` directories existed but contained no project guidance.
- Camera source, scripts, binary artifacts, and Russian documentation already existed under `camera-ov5647/`.
- `build/` and `linux-orangepi-sun60iw2/` were independent nested Git repositories.

## Documentation basis

The official Codex documentation states that Codex loads `AGENTS.md` from the project root down to the current working directory, with more specific nested instructions taking precedence. It also documents a default combined instruction limit of 32 KiB. Based on that behavior, stable instructions were kept concise and evolving history was placed in normal Markdown documentation.

Official reference:

- [Custom instructions with AGENTS.md](https://learn.chatgpt.com/docs/agent-configuration/agents-md.md)

## Created structure

```text
AGENTS.md
camera-ov5647/AGENTS.md
docs/
├── README.md
├── agent-context/
│   ├── ENVIRONMENT.md
│   ├── PROJECT_MAP.md
│   └── WORKFLOW.md
├── worklog/
├── decisions/
├── runbooks/
├── handoffs/
└── templates/
```

## Key design choices

### Concise automatic instructions

The root `AGENTS.md` defines mission, safety, workflow, reporting, and navigation. It links to detailed context instead of embedding all historical results.

### Scoped camera instructions

`camera-ov5647/AGENTS.md` records only the constraints that must be active while modifying camera files: three DMA buffers, a single V4L2 process, FIFO isolation, bounded tests, and required evidence.

### Durable knowledge types

- `agent-context/`: relatively stable environment and layout facts.
- `worklog/`: chronological commands, evidence, failures, and results.
- `decisions/`: constraints future implementations should respect.
- `runbooks/`: verified operational procedures.
- `handoffs/`: concise continuation state for another agent/session.
- `templates/`: reporting and transition standards.

## Populated knowledge

The initial knowledge base includes:

- a consolidated OV5647 bring-up report;
- an OV5647 operational runbook;
- ADR-0001 requiring three DMA buffers;
- ADR-0002 requiring one V4L2 session and FIFO raw-data isolation;
- a current handoff describing the working camera stream and next tasks;
- task-report, ADR, and handoff templates.

## Validation

Commands ran on the local workstation from `/home/artm1904/Program/Robot/os`.

```bash
wc -c AGENTS.md camera-ov5647/AGENTS.md
```

Result:

```text
4472 AGENTS.md
1818 camera-ov5647/AGENTS.md
6290 total
```

The combined instructions are well below the documented default 32 KiB limit.

A local link-integrity check inspected all new Markdown files and reported zero missing relative targets.

## Files created or changed

- `/home/artm1904/Program/Robot/os/AGENTS.md`
- `/home/artm1904/Program/Robot/os/camera-ov5647/AGENTS.md`
- `/home/artm1904/Program/Robot/os/docs/README.md`
- `/home/artm1904/Program/Robot/os/docs/agent-context/*`
- `/home/artm1904/Program/Robot/os/docs/worklog/*`
- `/home/artm1904/Program/Robot/os/docs/decisions/*`
- `/home/artm1904/Program/Robot/os/docs/runbooks/*`
- `/home/artm1904/Program/Robot/os/docs/handoffs/*`
- `/home/artm1904/Program/Robot/os/docs/templates/*`

No package was installed, no service was changed, and no SBC command was executed for this task.

## Usage

Start a new agent session from the workspace root or a subsystem directory. The root instructions should load automatically; a session started in `camera-ov5647/` should additionally load the nested camera instructions.

Relevant detailed reports should be read on demand rather than all at once.

## Limitations and next steps

- The structure depends on agents following linked navigation instructions; only `AGENTS.md` files are automatically loaded.
- Other subsystems should receive nested `AGENTS.md` only when they develop genuinely different commands or safety constraints.
- A project `.codex/config.toml` was intentionally not added because no repository-specific model, sandbox, MCP, or hook setting was required.
- Future work can add mechanical validation scripts or hooks after the report workflow has been exercised manually.

