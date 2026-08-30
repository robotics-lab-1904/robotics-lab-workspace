# Project Map

## Workspace layout

```text
os/
├── AGENTS.md                       Root agent contract
├── camera-ov5647/                  Camera artifacts and scoped instructions
├── linux-orangepi-sun60iw2/        Independent vendor-kernel Git repository
├── build/                           Independent Armbian build Git repository
├── docs/                            Shared knowledge base
│   ├── agent-context/               Stable context
│   ├── worklog/                     Chronological reports
│   ├── decisions/                   ADRs
│   ├── runbooks/                    Tested procedures
│   ├── handoffs/                    Continuation state
│   └── templates/                   Document templates
└── ROBOTICS_LAB_SYSTEM_PROMPT_RU.md Historical Russian long-form prompt
```

## Repository boundaries

Before Git operations, run:

```bash
git rev-parse --show-toplevel
git status --short
```

Known independent repositories:

- `build/` — Armbian build framework and outputs.
- `linux-orangepi-sun60iw2/` — Allwinner/Orange Pi vendor kernel source.

The workspace root is used as a lab coordination and documentation layer. Do not assume a root Git operation includes changes inside the nested repositories.

## Ownership of information

- Stable behavioral rules belong in `AGENTS.md`.
- Machine and hardware facts belong in `docs/agent-context/ENVIRONMENT.md`.
- Commands and evidence from one task belong in `docs/worklog/`.
- Durable implementation choices belong in `docs/decisions/`.
- Repeatable operations belong in `docs/runbooks/`.
- Incomplete current state belongs in `docs/handoffs/CURRENT.md`.
- Source code and generated artifacts remain in their subsystem directories.

