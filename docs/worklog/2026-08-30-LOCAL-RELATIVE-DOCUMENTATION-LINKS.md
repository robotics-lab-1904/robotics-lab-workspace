# Local Relative Documentation Links

- Date: 2026-08-30
- Status: Completed locally; commits and pushes pending
- Owner/agent: Codex
- Related issue/task: Adopt option 2 for internal Markdown links

## Objective

Make the recursive superproject checkout the canonical documentation graph and
replace internal cross-repository GitHub navigation links with local relative
Markdown links.

## Success criteria

- Internal documentation links resolve through the local filesystem.
- Submodule instructions refer to shared superproject context relatively.
- External sources, clone URLs, remotes, and historical commands retain their
  real URLs.
- The link policy is recorded as a durable ADR.

## Environment

### Local workstation

- Workspace: `/home/artm1904/Program/Robot/robotics-lab-workspace`
- Superproject branch: `main`
- Camera submodule branch: `main`

### Target hardware

No board or hardware operation was performed.

### Software versions

No packages were installed, removed, or upgraded.

## Initial state

The camera submodule used GitHub `blob/main` links for the superproject's root
instructions, camera runbook, ADRs, and bring-up report. The root README linked
internal submodules back to their GitHub repository pages.

## Safety and rollback plan

Only Markdown files are changed. Camera documentation is modified inside its
independent submodule and must be committed there before its superproject
gitlink is updated.

## Theory and references

Relative local links provide offline access and bind navigation to the current
checkout. Cross-submodule relative links trade away standalone submodule
rendering; this is accepted because the recursive superproject is canonical.

## Plan

1. Inventory internal organization URLs.
2. Convert navigation links while preserving operational URLs.
3. Add ADR-0003 and update indexes.
4. Validate every relative Markdown target from the superproject root.

## Installed or changed packages

| Package | Version | Source | Reason | Direct/dependency |
|---|---|---|---|---|
| None | — | — | Documentation-only task | — |

## Created or changed files

| Path | Change | Repository |
|---|---|---|
| `AGENTS.md` | Added local-link policy | Superproject |
| `README.md` | Replaced internal repository links and added ADR entry | Superproject |
| `docs/README.md` | Documented link policy | Superproject |
| `docs/decisions/README.md` | Indexed ADR-0003 | Superproject |
| `docs/decisions/ADR-0003-LOCAL-RELATIVE-DOCUMENTATION-LINKS.md` | Created decision record | Superproject |
| `docs/worklog/README.md` | Indexed this report | Superproject |
| `camera-ov5647/AGENTS.md` | Replaced cross-repository HTTP links | Camera submodule |
| `camera-ov5647/README.md` | Linked the local kernel submodule | Camera submodule |

## Commands executed

All commands ran on the workstation from the superproject root.

```bash
rg -n --glob '*.md' -g '!third_party/**' \
  'https://github.com/robotics-lab-1904/' .
git status --short --branch
git -C camera-ov5647 status --short --branch
```

Purpose: locate internal HTTP navigation links and preserve existing unrelated
work in each repository.

## Experiments

No hardware experiment was performed.

## Errors and diagnosis

None at the time of writing.

## Rejected hypotheses

- **Rejected:** all HTTP URLs should be replaced. Clone commands, remotes,
  upstream citations, and historical evidence require real URLs.
- **Rejected:** duplicated documentation is safer than cross-boundary paths.
  Duplication creates competing sources of truth.

## Validation

- Scanned 29 maintained Markdown files from the superproject root.
- Found zero missing relative-link targets.
- Found zero Markdown links to internal `robotics-lab-1904` GitHub pages.
- Remaining organization URLs occur only in clone commands, remote examples,
  source text, validation patterns, or historical evidence.
- `git diff --check` passed in both the superproject and camera submodule.

## Final result

Internal Markdown navigation is now local-relative throughout the maintained
superproject and initialized submodule documentation. The recursive
superproject checkout is the single canonical documentation environment.

## Limitations and open questions

- Internal links from a submodule do not render when that submodule is cloned or
  browsed independently.
- Registered submodule paths are now part of the documentation contract.

## Reproduction from a clean state

```bash
git clone --recurse-submodules \
  https://github.com/robotics-lab-1904/robotics-lab-workspace.git
```

## Rollback

Restore the changed Markdown files in their owning repositories. Do not reset
unrelated work.

## Next steps

1. Commit and push the camera documentation changes.
2. Commit the updated camera gitlink and superproject documentation.

## Learning topics

- Relative Markdown URL resolution
- Git submodule repository boundaries
- Documentation ownership and version drift

## Sources

- [ADR-0003](../decisions/ADR-0003-LOCAL-RELATIVE-DOCUMENTATION-LINKS.md)
