# Workspace Link and Path Migration

- Date: 2026-08-30
- Status: Completed locally; commits and pushes pending
- Owner/agent: Codex
- Related issue/task: Align repository content with the completed submodule migration

## Objective

Update current documentation, paths, repository links, and agent context for
the active `robotics-lab-workspace` superproject and its four submodules.

## Success criteria

- Current documents use the active workspace root and submodule paths.
- `.gitmodules` parses and all four gitlinks resolve to their intended remotes.
- Current documentation contains no stored SSH password.
- Local Markdown links resolve, and cross-repository links use durable GitHub
  URLs where appropriate.
- Historical reports remain faithful to the paths where commands originally ran.

## Environment

### Local workstation

- Superproject: `/home/artm1904/Program/Robot/robotics-lab-workspace`
- Branch before edits: `main`
- Initial commit: `c8cd341`

### Target hardware

No board commands or hardware changes were made.

### Software versions

Git `2.55.0`; no packages were installed, removed, or upgraded.

## Initial state

**Observed:** `.gitmodules` was valid at `c8cd341`, and all four submodules were
initialized at their recorded commits.

**Observed:** current context still identified `/home/artm1904/Program/Robot/os`
as the workspace, described old independent repository paths, and stored an SSH
password contrary to `AGENTS.md`.

**Observed:** the standalone camera repository linked to `../docs`, which only
works when nested in the superproject and is broken when cloned independently.

**Observed:** historical worklogs contain old paths. These are evidence, not
current operating instructions, and were deliberately retained.

## Safety and rollback plan

- Do not modify source code, kernel commits, submodule remotes, or pinned
  commits as part of the content audit.
- Treat edits inside `camera-ov5647` as changes to a separate repository.
- Review and commit the camera repository first, then update its superproject
  gitlink.
- Roll back uncommitted documentation edits with targeted file restoration;
  never reset unrelated work.

## Theory and references

Git submodules are independent repositories. The superproject stores a gitlink
to one exact commit and `.gitmodules` stores clone URLs and optional update
branches. A relative Markdown path cannot cross from a standalone submodule
repository into a superproject that may not exist, so durable GitHub links are
used for shared lab documentation.

## Plan

1. Inventory repository state and stale paths.
2. Update active context, map, prompt, runbook, handoff, and indexes.
3. Update camera repository paths and cross-repository links.
4. Validate Git configuration, submodules, Markdown links, and diffs.

## Installed or changed packages

| Package | Version | Source | Reason | Direct/dependency |
|---|---|---|---|---|
| None | — | — | Documentation and repository metadata audit | — |

## Created or changed files

| Path | Change | Purpose | Repository | Rollback |
|---|---|---|---|---|
| `/home/artm1904/Program/Robot/robotics-lab-workspace/README.md` | Created | Entry point and submodule map | Superproject | Remove before commit or revert later commit |
| `/home/artm1904/Program/Robot/robotics-lab-workspace/AGENTS.md` | Updated | Describe submodule commit workflow | Superproject | Restore prior version |
| `/home/artm1904/Program/Robot/robotics-lab-workspace/ROBOTICS_LAB_SYSTEM_PROMPT_RU.md` | Updated | Active paths and secret policy | Superproject | Restore prior version |
| `/home/artm1904/Program/Robot/robotics-lab-workspace/docs/agent-context/ENVIRONMENT.md` | Updated | Active root, Git checks, and credential handling | Superproject | Restore prior version |
| `/home/artm1904/Program/Robot/robotics-lab-workspace/docs/agent-context/PROJECT_MAP.md` | Updated | Current superproject/submodule layout | Superproject | Restore prior version |
| `/home/artm1904/Program/Robot/robotics-lab-workspace/docs/handoffs/CURRENT.md` | Updated | Current pins, remaining work, credential rotation | Superproject | Restore prior version |
| `/home/artm1904/Program/Robot/robotics-lab-workspace/docs/runbooks/GIT_SUBMODULE_AND_KERNEL_FORK.md` | Updated | Mark migration outcome and active patch model | Superproject | Restore prior version |
| `/home/artm1904/Program/Robot/robotics-lab-workspace/docs/worklog/2026-08-30-GIT-REPOSITORY-MIGRATION-PLAN.md` | Appended | Preserve historical plan and record completion | Superproject | Restore prior version |
| `/home/artm1904/Program/Robot/robotics-lab-workspace/docs/worklog/2026-08-29-AI-AGENT-WORKSPACE-STRUCTURE.md` | Added notice | Distinguish historical paths from the active root | Superproject | Remove notice |
| `/home/artm1904/Program/Robot/robotics-lab-workspace/docs/worklog/2026-08-29-ULN2003-STEPPER-CLI.md` | Added notice | Identify the maintained stepper submodule | Superproject | Remove notice |
| `/home/artm1904/Program/Robot/robotics-lab-workspace/docs/worklog/README.md` | Updated | Index important reports | Superproject | Restore prior version |
| `/home/artm1904/Program/Robot/robotics-lab-workspace/patches/armbian/apply_patch.sh` | Rewritten | Safe path-independent check/apply helper | Superproject | Restore prior two-command helper |
| `/home/artm1904/Program/Robot/robotics-lab-workspace/camera-ov5647/AGENTS.md` | Updated | Durable cross-repository links | Camera submodule | Restore in camera repository |
| `/home/artm1904/Program/Robot/robotics-lab-workspace/camera-ov5647/README.md` | Updated | Link maintained kernel fork | Camera submodule | Restore in camera repository |
| `/home/artm1904/Program/Robot/robotics-lab-workspace/camera-ov5647/OV5647_FULL_GUIDE_RU.md` | Updated | Current workspace, kernel, and Armbian paths | Camera submodule | Restore in camera repository |

## Commands executed

All commands ran on the workstation from the superproject root.

```bash
git status --short --branch
git log -3 --oneline --decorate
git submodule status --recursive
git submodule foreach --recursive 'git status --short --branch'
git config --local --get-regexp '^submodule\.'
rg -n <stale-path-and-link-patterns> .
```

Purpose: establish exact repository boundaries, pins, dirty state, URLs, stale
paths, Markdown links, and potential stored credentials.

## Experiments

No hardware experiment was performed.

## Errors and diagnosis

- A combined validation command failed before executing because of unmatched
  shell quoting. It made no changes; the checks were rerun as isolated commands.
- Direct execution of `patches/armbian/apply_patch.sh --check` initially failed
  with exit status 126 because the old helper had no shebang and was not
  executable. The helper was converted into a path-independent Bash script.
  The current filesystem did not permit changing its executable mode, so the
  documented invocation is `bash patches/armbian/apply_patch.sh --check`.
- Content inconsistencies resulted from the workspace migration completing
  after the original documentation was written.

## Rejected hypotheses

- **Rejected:** every old absolute path should be replaced mechanically.
  Historical reports must preserve where commands originally ran.
- **Rejected:** submodule file changes can be committed only in the
  superproject. They require a commit in the submodule repository first.

## Validation

- `.gitmodules` parsed all 12 path, URL, and branch values.
- All four submodules were initialized at their recorded gitlinks.
- `git ls-remote` confirmed that every configured branch head matched the
  pinned commit at validation time.
- 27 non-vendor Markdown files were scanned; no missing relative link was found.
- Current files contained no explicit stored SSH credential pattern.
- `git diff --check` passed in the superproject and all inspected submodules.
- `bash -n patches/armbian/apply_patch.sh` passed.
- `bash patches/armbian/apply_patch.sh --check` confirmed that the Armbian patch
  applies cleanly without modifying the submodule.

## Final result

Current operational documentation now describes the active superproject and
submodule layout. Repository and branch links resolve to the commits pinned by
the superproject. Historical worklogs retain their original paths and are
explicitly distinguished from current instructions.

### Link-policy correction — 2026-08-30

This task initially changed camera cross-repository references to GitHub
`blob/main` URLs so the camera repository could render them standalone. The
user subsequently selected the opposite tradeoff: the recursive superproject
checkout is canonical, and internal documentation must use local relative
links. ADR-0003 supersedes the earlier cross-repository URL choice. External
Git commands, remotes, and sources continue to use HTTP URLs.

## Limitations and open questions

- External HTTP links can change independently and require separate network
  validation if exhaustive availability checking is needed.
- Historical reports intentionally retain legacy paths.
- The previous SSH password remains present in Git history at commit `5f5ac26`.
  It must be rotated; current-file removal alone is not credential revocation.
- The filesystem rejected changing `patches/armbian/apply_patch.sh` to mode
  `100755`, so invoke it explicitly through `bash`.

## Reproduction from a clean state

```bash
git clone --recurse-submodules \
  https://github.com/robotics-lab-1904/robotics-lab-workspace.git
```

Then run the validation commands recorded in this report.

## Rollback

Restore only the files listed in the finalized changed-files table. Camera
documentation must be restored within the camera submodule repository.

## Next steps

1. Rotate the exposed historical SSH credential.
2. Commit and push camera documentation in its repository.
3. Commit the updated camera gitlink and superproject documentation.

## Learning topics

- Git submodule gitlinks and detached HEAD states
- Cross-repository documentation links
- Immutable worklogs versus mutable runbooks
- Secret handling in infrastructure documentation

## Sources

- https://git-scm.com/docs/git-submodule
