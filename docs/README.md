# Robotics Lab Knowledge Base

This directory contains durable knowledge for humans and AI agents.

| Directory | Purpose | Update frequency |
|---|---|---|
| `agent-context/` | Stable environment, project map, and workflow | When infrastructure changes |
| `worklog/` | Chronological task reports and experiment evidence | Every substantive task |
| `decisions/` | Architecture Decision Records (ADRs) | When a durable choice is made |
| `runbooks/` | Tested operational procedures | When procedures change |
| `handoffs/` | Current state and continuation notes | At unfinished task boundaries |
| `templates/` | Standard document templates | Rarely |

`AGENTS.md` files contain concise instructions automatically loaded by compatible agents. This knowledge base contains detailed and evolving information that agents should read only when relevant.

## Naming conventions

- Worklog: `YYYY-MM-DD-SHORT-TASK-NAME.md`
- ADR: `ADR-NNNN-SHORT-DECISION.md`
- Runbook: `SUBSYSTEM_OR_OPERATION.md`
- Handoff archive: `YYYY-MM-DD-SHORT-TASK-NAME.md`

Use English for instructions, reports, filenames, commit messages, and newly created technical documentation unless the user explicitly requests another language.

## Link policy

Use local relative Markdown links for documents and files that exist in the
canonical superproject checkout, including paths that cross into or out of a
submodule. Keep HTTP URLs for external sources, Git clone/remotes, and historical
command evidence. See
[ADR-0003](decisions/ADR-0003-LOCAL-RELATIVE-DOCUMENTATION-LINKS.md).
