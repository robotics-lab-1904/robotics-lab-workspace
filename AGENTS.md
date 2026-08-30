# Robotics Lab Repository Instructions

## Mission

This workspace is a practical robotics laboratory. Optimize for verified learning, reproducible experiments, and safe interaction with real hardware—not merely for producing code quickly.

Explain important mechanisms and tradeoffs while completing the requested work. Clearly distinguish observed facts, hypotheses, and conclusions.

## Required context

Before hardware, kernel, camera, ROS, NPU, or board-level work, read the relevant files:

- `docs/agent-context/ENVIRONMENT.md` — hosts, operating systems, hardware, and known constraints.
- `docs/agent-context/PROJECT_MAP.md` — repository layout and ownership boundaries.
- `docs/agent-context/WORKFLOW.md` — experiment, validation, reporting, and handoff process.
- `docs/runbooks/` — subsystem-specific operating procedures.
- `docs/decisions/` — decisions that constrain implementation choices.
- `docs/handoffs/CURRENT.md` — current state and unfinished work.

Read only the reports relevant to the task. Do not load the entire history by default.

## Work rules

1. Inspect the current state before changing it. Hardware, OS images, kernels, device names, and network addresses may change.
2. Make one logical change at a time and validate it proportionally to risk.
3. Use staged experiments: detection → minimal operation → bounded load → sustained load → integration → service → autostart.
4. Preserve user changes and independent nested repositories. Never assume the workspace root and nested Git repositories share history.
5. Back up working DTBs, boot files, kernel modules, firmware, and service definitions before replacing them.
6. Do not perform risky remote boot or hardware changes unless a recovery path is available.
7. Never store passwords, tokens, private keys, or other secrets. Use placeholders such as `<PASSWORD>`.
8. Use primary documentation, datasheets, schematics, reference manuals, official source code, and measured results where possible.
9. Prefer `rg` and `rg --files` for local discovery.
10. Keep generated binaries, raw captures, build outputs, and logs separate from source documentation when practical.

## Documentation contract

Every substantive task must create or update a Markdown report under `docs/worklog/`. Use `docs/templates/TASK_REPORT_TEMPLATE.md`.

Reports must include:

- objective and success criteria;
- date and verified environment;
- initial state;
- commands executed and where they ran;
- installed, removed, or upgraded packages and versions;
- files created or changed, with absolute target paths where relevant;
- test procedure, output, measurements, and exit status when useful;
- failures, rejected hypotheses, and supporting evidence;
- result, limitations, rollback, and next steps;
- sources and recommended learning topics.

Update `docs/handoffs/CURRENT.md` when work remains unfinished or another agent needs to continue it. Create an ADR under `docs/decisions/` for choices that should constrain future work.

Do not use `AGENTS.md` as a chronological log. Keep it short, stable, and actionable; put evolving results in reports, ADRs, runbooks, and handoffs.

## Validation and reporting

- Lead final responses with the practical outcome.
- State exactly what was changed and what was not changed.
- Provide commands to reproduce and verify the result.
- If a test was not run, say so and explain why.
- Treat warnings in vendor kernels contextually; do not label them as root causes without evidence.
- When correcting an earlier assumption, retain the history in the task report and explain what evidence changed the conclusion.

## Hardware safety

- Power down before changing CSI/FPC, GPIO, I2C, SPI, motor, relay, or power wiring unless hot-plug support is explicitly documented.
- Verify connector pitch, contact count, orientation, pinout, voltage, and common ground.
- Do not guess regulator, clock, reset, GPIO, or pinctrl assignments.
- Stop immediately on overheating, smell, unstable power, repeated resets, or disappearing power indicators.
- Do not drive motors, relays, heaters, or other loads directly from GPIO.
- For failures that can remove SSH, prefer UART, persistent journal, pstore/ramoops, netconsole, or another out-of-band diagnostic path.

## Scope-specific instructions

Nested `AGENTS.md` files may add constraints for their subtree. Instructions closer to the edited file take precedence over this file where they conflict.

