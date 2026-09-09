# Project Map

## Workspace layout

```text
robotics-lab-workspace/
├── .gitmodules                         Submodule URLs and update branches
├── AGENTS.md                           Root agent contract
├── README.md                           Human entry point
├── camera-ov5647/                      Submodule: camera project
├── stepper-motor/                      Submodule: motor project
├── ros-packages/                       ROS 2 source repo; parent gitlink not yet recorded
├── third_party/
│   ├── armbian-build/                  Submodule: upstream Armbian build
│   └── linux-orangepi-sun60iw2/        Submodule: OV5647 kernel fork
├── patches/armbian/                    Patch applied to Armbian submodule
├── docs/                               Shared knowledge base
│   ├── agent-context/                  Stable context
│   ├── worklog/                        Chronological reports
│   ├── decisions/                      ADRs
│   ├── runbooks/                       Tested procedures
│   ├── handoffs/                       Continuation state
│   └── templates/                      Document templates
└── ROBOTICS_LAB_SYSTEM_PROMPT_RU.md    Historical Russian long-form prompt
```

## Repository boundaries

Before Git operations, run:

```bash
git rev-parse --show-toplevel
git status --short
```

Known submodule repositories:

- `camera-ov5647/` — `robotics-lab-1904/camera-ov5647`, branch `main`.
- `stepper-motor/` — `robotics-lab-1904/stepper-motor`, branch `main`.
- `ros-packages/` — `robotics-lab-1904/ros-packages`, branch configured as `main`.
  On 2026-09-09 it has a `.git` file pointing to the parent's submodule Git
  storage and a `.gitmodules` entry, but no parent index gitlink yet. Treat it
  as an independent repository; do not add its source files into the parent.
- `third_party/armbian-build/` — upstream `armbian/build`, branch `main`.
- `third_party/linux-orangepi-sun60iw2/` — organization fork
  `robotics-lab-1904/linux-orangepi`, branch `robotics/ov5647-sun60iw2`.

The workspace root is the superproject. A root commit records only each
submodule commit ID, not file changes made inside a submodule. Commit and push
submodule changes in their own repositories first, then commit the updated
gitlink in the superproject.

The original `/home/artm1904/Program/Robot/os` tree is legacy migration source,
not the active workspace. Historical reports retain its paths as evidence of
where commands originally ran.

## Ownership of information

- Stable behavioral rules belong in `AGENTS.md`.
- Machine and hardware facts belong in `docs/agent-context/ENVIRONMENT.md`.
- Commands and evidence from one task belong in `docs/worklog/`.
- Durable implementation choices belong in `docs/decisions/`.
- Repeatable operations belong in `docs/runbooks/`.
- Incomplete current state belongs in `docs/handoffs/CURRENT.md`.
- Source code and generated artifacts remain in their subsystem directories.
- `ros-packages/` contains multiple ROS 2 packages; link it under each host's
  own colcon workspace `src/`. Share source via Git and build separately per
  architecture. Ignore build/install/log and local `.validation` artifacts.
