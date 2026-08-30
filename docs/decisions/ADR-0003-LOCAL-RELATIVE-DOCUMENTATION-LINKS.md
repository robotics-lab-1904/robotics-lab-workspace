# ADR-0003: Use Local Relative Links for Workspace Documentation

- Status: Accepted
- Date: 2026-08-30
- Decision owners: Robotics Lab workspace maintainers

## Context

The workspace is a Git superproject with camera, stepper-motor, Armbian, and
vendor-kernel submodules. Some subsystem documentation previously linked back
to the superproject through GitHub `blob/main` URLs. Those links worked in a
standalone submodule clone but required network access and could resolve to
documentation newer than the locally pinned source.

The canonical operating environment is a recursive checkout of
`robotics-lab-workspace`, where both the superproject documents and all
submodules are present.

## Decision

Use local relative Markdown links for any file present in the canonical
superproject checkout, including links across a submodule boundary.

Use HTTP URLs only when the target is genuinely external, or when the URL is
part of an operational Git command, remote definition, source citation, or
historical record.

Submodule documentation may therefore assume its registered location in the
superproject. For example, `camera-ov5647/AGENTS.md` may link to the shared
camera runbook as `../docs/runbooks/OV5647_CAMERA.md`.

## Consequences

### Positive

- Agents can read and search documentation without network access.
- Links resolve to the same checkout being inspected.
- Documentation does not silently drift to a newer `main` branch.
- Link validation can check the local filesystem deterministically.

### Negative

- Cross-boundary links do not resolve in a standalone submodule clone or on the
  submodule repository's GitHub page.
- Submodules must remain at their registered paths in the canonical workspace.
- A recursive clone is required for the complete documentation graph.

## Alternatives considered

### GitHub links to `blob/main`

Rejected for internal navigation because they require network access and may
not match the checked-out commits.

### Immutable GitHub commit permalinks

More reproducible than `main`, but still network-dependent and expensive to
maintain whenever documentation changes.

### Duplicate shared documentation in every submodule

Rejected because duplicated instructions can diverge and create ambiguous
sources of truth.

## Validation

Run the local Markdown-link validator described in the associated worklog and
confirm that it reports zero missing relative links from the superproject root.

## Related material

- [Project map](../agent-context/PROJECT_MAP.md)
- [Agent workflow](../agent-context/WORKFLOW.md)
- [Current handoff](../handoffs/CURRENT.md)

