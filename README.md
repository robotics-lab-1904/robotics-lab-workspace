# Robotics Lab Workspace

Practical laboratory for embedded Linux, robotics, camera drivers, ROS 2, NPU
experiments, microcontrollers, electronics, and reproducible hardware research.

## Repository layout

| Local path | Pinned branch | Purpose |
|---|---|---|
| [`camera-ov5647/`](camera-ov5647/) | `main` | OV5647 tools, artifacts, and subsystem documentation |
| [`stepper-motor/`](stepper-motor/) | `main` | ULN2003 stepper-motor controller and tests |
| [`third_party/armbian-build/`](third_party/armbian-build/) | `main` | Pinned upstream Armbian build framework |
| [`third_party/linux-orangepi-sun60iw2/`](third_party/linux-orangepi-sun60iw2/) | `robotics/ov5647-sun60iw2` | Pinned Orange Pi vendor kernel fork with OV5647 support |
| [`patches/armbian/`](patches/armbian/) | — | Lab-specific Armbian patch and application helper |
| [`docs/`](docs/) | — | Context, runbooks, decisions, worklogs, and handoffs |

The four source directories above are Git submodules. The superproject pins an
exact commit for each one; the branch names in [`.gitmodules`](.gitmodules) are
update hints and do not override those pins.

## Clone

```bash
git clone --recurse-submodules \
  https://github.com/robotics-lab-1904/robotics-lab-workspace.git
```

For an existing clone:

```bash
git submodule sync --recursive
git submodule update --init --recursive
```

## Start here

- [Agent instructions](AGENTS.md)
- [Environment](docs/agent-context/ENVIRONMENT.md)
- [Project map](docs/agent-context/PROJECT_MAP.md)
- [Workflow](docs/agent-context/WORKFLOW.md)
- [Current handoff](docs/handoffs/CURRENT.md)
- [ROS 2 face tracking on Orange Pi](docs/runbooks/ROS2_FACE_TRACKING_ORANGE_PI.md)
- [Submodule runbook](docs/runbooks/GIT_SUBMODULE_AND_KERNEL_FORK.md)
- [ADR-0003: local relative documentation links](docs/decisions/ADR-0003-LOCAL-RELATIVE-DOCUMENTATION-LINKS.md)

Do not commit credentials, raw captures, generated images, build caches, or
other replaceable artifacts to the superproject.

`linux.txt` is retained as legacy, unstructured shell-command history. It is
not a current runbook; use the procedures under [`docs/runbooks/`](docs/runbooks/)
for reproducible work.
