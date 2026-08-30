# Git Repository Migration Plan

- Date: 2026-08-30
- Status: In progress
- Owner/agent: Codex
- Related issue/task: Publish Armbian and modified Orange Pi kernel through the robotics lab superproject

## Objective

Produce an exact, non-destructive procedure for adding the Armbian build system
as a submodule and publishing the modified Orange Pi vendor kernel through an
organization fork while preserving all local changes.

## Success criteria

- Identify every dirty repository before proposing migration commands.
- Preserve the OV5647 kernel source, DTS, Kconfig, Makefile, Armbian config, and
  Armbian device-tree patch.
- Define correct `origin` and `upstream` semantics.
- Pin both dependencies as submodules in `robotics-lab-workspace`.
- Include clean-clone validation and rollback procedures.

## Environment

### Local workstation

- Main repository: `/home/artm1904/Program/Robot/robotics-lab-workspace`
- Original lab workspace: `/home/artm1904/Program/Robot/os`
- Git: `2.55.0`
- GitHub CLI: not installed

### Target hardware

No target-board commands or hardware changes were required.

### Software versions

No packages were installed, removed, or upgraded.

## Initial state

**Observed:** The main repository is clean on `main` at `5f5ac26` and uses
`https://github.com/robotics-lab-1904/robotics-lab-workspace.git` as `origin`.

**Observed:** `/home/artm1904/Program/Robot/os/build` is on `main` at
`de5fd0aeb69d1670f8d2894c4f06cca931feba9b`, with two modified tracked files.
Its current `origin` is `https://github.com/armbian/build.git`.

**Observed:** `/home/artm1904/Program/Robot/os/linux-orangepi-sun60iw2` is on
`orange-pi-6.6-sun60iw2` at `8a9be72c9006a87f786736b3aa4e2dfd971c1429`.
It has three modified tracked files and the untracked OV5647 driver. Its current
`origin` is `https://github.com/orangepi-xunlong/linux-orangepi.git`.

**Conclusion:** Converting either working directory directly into a clean
submodule before preserving and publishing its changes risks losing work or
creating a non-reproducible dirty submodule.

## Safety and rollback plan

- No remotes, branches, commits, or GitHub repositories were changed in this
  planning task.
- The runbook creates binary-safe diffs and separately copies untracked
  `ov5647.c` before any remote changes.
- Existing repositories are retained until a clean second clone passes.
- Remote renames can be reversed without changing files or commits.

## Theory and references

A superproject records an exact submodule commit. A configured submodule branch
is used for remote-update behavior, but normal submodule checkout uses the
recorded commit. A fork should use the organization repository as `origin` and
the original project as `upstream`.

## Plan

1. Back up dirty tracked and untracked work.
2. Create the Orange Pi kernel fork in `robotics-lab-1904`.
3. Commit the OV5647 work on `robotics/ov5647-sun60iw2` and push it.
4. Choose an Armbian preservation model: fork (recommended) or tracked patch.
5. Add fresh submodule clones under `third_party/`.
6. Commit the pins and validate from a clean clone.

## Installed or changed packages

| Package | Version | Source | Reason | Direct/dependency |
|---|---|---|---|---|
| None | — | — | Planning and documentation only | — |

## Created or changed files

| Path | Change | Purpose | Owner/mode | Rollback |
|---|---|---|---|---|
| `/home/artm1904/Program/Robot/robotics-lab-workspace/docs/runbooks/GIT_SUBMODULE_AND_KERNEL_FORK.md` | Created | Reproducible migration procedure | Repository default | Delete before commit or revert its future commit |
| `/home/artm1904/Program/Robot/robotics-lab-workspace/docs/worklog/2026-08-30-GIT-REPOSITORY-MIGRATION-PLAN.md` | Created | Evidence and task history | Repository default | Delete before commit or revert its future commit |
| `/home/artm1904/Program/Robot/robotics-lab-workspace/docs/handoffs/CURRENT.md` | Updated | Record pending external and Git operations | Repository default | Restore previous version or revert its future commit |

## Commands executed

Commands ran on the workstation. Read-only inspection included:

```bash
git -C <repository> status --short --branch
git -C <repository> remote -v
git -C <repository> branch --show-current
git -C <repository> rev-parse HEAD
git -C <repository> diff --stat
du -sh build linux-orangepi-sun60iw2 robotics-lab-workspace
git --version
gh auth status
```

Purpose: establish repository boundaries, dirty state, remotes, exact base
commits, approximate sizes, and tool availability.

Result: all preservation-critical changes were identified. Some `du` reads in
the Armbian APT cache returned permission errors, but the repository total was
still approximately 3.1 GiB; this does not affect the migration design.

## Experiments

No code or hardware experiment was performed.

## Errors and diagnosis

- `gh` returned `command not found`. Diagnosis: GitHub CLI is not installed.
  The runbook uses the GitHub web interface instead.
- `du` could not read several root-owned APT cache directories. This only makes
  the reported size approximate and does not indicate repository corruption.

## Rejected hypotheses

- **Rejected:** The Armbian checkout can immediately become a clean upstream
  submodule. Evidence: it has two uncommitted OV5647-related modifications.
- **Rejected:** `git diff` alone backs up all kernel work. Evidence: `ov5647.c`
  is untracked and is therefore absent from ordinary `git diff` output.

## Validation

The instructions were checked against the observed paths, branches, remotes,
and current Git submodule syntax. The migration itself was not executed because
fork creation, commits, and pushes change external state and were not requested
as actions in this task.

## Final result

A detailed runbook now defines safe backup, fork creation, remote configuration,
targeted commits, submodule creation, clean-clone validation, daily use, upstream
synchronization, and rollback.

## Limitations and open questions

- The exact URL of the kernel fork is unknown until it is created.
- The user must choose whether to fork Armbian (recommended) or maintain its two
  local changes as a patch in the superproject.
- No GitHub authentication or push was tested.
- No full kernel or Armbian build was performed.

## Reproduction from a clean state

Follow `docs/runbooks/GIT_SUBMODULE_AND_KERNEL_FORK.md`, including its independent
clone validation phase.

## Rollback

No operational changes were made. Remove the documentation files and restore
the handoff if this plan should be discarded.

## Next steps

1. Create the kernel fork under `robotics-lab-1904`.
2. Run the backup phase.
3. Publish the kernel branch.
4. Select and execute the Armbian preservation model.
5. Add and validate submodules.

## Learning topics

- Git object model and gitlinks (`mode 160000`)
- Detached HEAD behavior in submodules
- Fork remote conventions (`origin` versus `upstream`)
- Patch queues versus maintained forks
- Reproducible dependency pinning

## Sources

- https://git-scm.com/docs/git-submodule
- https://docs.github.com/en/pull-requests/how-tos/work-with-forks/fork-a-repo
- https://docs.github.com/en/pull-requests/how-tos/work-with-forks/configuring-a-remote-repository-for-a-fork

