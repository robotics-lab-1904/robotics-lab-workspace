# Agent Workflow

## Start of task

1. Read the root and applicable nested `AGENTS.md` files.
2. Read `ENVIRONMENT.md`, `PROJECT_MAP.md`, and `handoffs/CURRENT.md` when relevant.
3. Locate the correct Git repository and inspect its status.
4. Define the objective, success criteria, risk level, and rollback.
5. Create the task report from `docs/templates/TASK_REPORT_TEMPLATE.md`.

## During work

- Add commands and results to the report while evidence is fresh.
- Record whether each command ran on the workstation or the SBC.
- Capture package versions and exact file paths.
- Keep observations, hypotheses, and conclusions explicitly separate.
- Use bounded tests before sustained or automated operation.
- Update an ADR when a choice becomes a constraint for future work.
- Update a runbook only after the procedure is validated.

## End of task

1. Run appropriate validation.
2. Review diffs and unrelated user changes.
3. Complete results, rollback, limitations, and learning resources in the report.
4. Update `docs/handoffs/CURRENT.md` if anything remains unfinished.
5. Archive a completed handoff when useful.
6. In the final response, link the report and the most important changed files.

## Evidence quality

Use these labels in reports when helpful:

- **Observed:** directly measured or present in logs/source.
- **Inferred:** best explanation supported by observations.
- **Unverified:** plausible but not yet tested.
- **Rejected:** contradicted by later evidence.

## Experiment IDs

For multi-step investigations, assign IDs such as `EXP-CAM-001`. Record:

- hypothesis;
- one changed variable;
- command or setup;
- measurements;
- result;
- interpretation;
- next experiment.

