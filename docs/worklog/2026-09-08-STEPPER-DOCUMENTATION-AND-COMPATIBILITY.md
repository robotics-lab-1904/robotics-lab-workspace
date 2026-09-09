# Stepper Documentation and Board Compatibility

- Date: 2026-09-08
- Status: Completed
- Owner/agent: Codex
- Related issue/task: Document ULN2003 motor work and system compatibility

## Objective

Convert the stepper experiment into durable, safe documentation covering the
verified Orange Pi environment, GPIO mapping, API compatibility, operation,
failure handling, rollback, and remaining hardware validation.

## Success criteria

- Provide a compatibility matrix grounded in live observations.
- Provide a staged operating runbook.
- Record the libgpiod 1.6/2.x design decision.
- Update environment, handoff, and existing motor documentation. The project
  map already describes the stepper submodule correctly and needs no change.
- Remove any stored authentication secret found during review.

## Environment

### Local workstation

- Canonical workspace: `/home/artm1904/Program/Robot/robotics-lab-workspace`
- Documentation inspected under `docs/` per `AGENTS.md`.

### Target hardware

- Orange Pi Zero 3W, AArch64, reachable using SSH key authentication.
- ULN2003 and motor wiring were not touched during this task.

### Software versions

- Armbian-unofficial 26.08.0-trunk, Ubuntu Noble base
- Kernel `6.6.98-vendor-sun60iw2`
- Python 3.12.3
- Python gpiod 1.6.3

## Initial state

The controller, README, and experiment report existed in the canonical
superproject/submodule checkout. Documentation lacked a dedicated compatibility
note, runbook, and ADR. The README also mentioned a removed `--lines` option.

## Safety and rollback plan

Only read live system/GPIO metadata; do not issue motion or GPIO request
commands. Documentation edits are individually reversible. No board files,
packages, services, wiring, or GPIO values are changed.

## Theory and references

The compatibility boundary spans board/SoC pin mapping, gpiochip ownership,
Python binding generation, electrical driver behavior, and non-real-time
userspace scheduling. Each layer is documented separately.

## Plan

1. Read repository documentation instructions and relevant existing reports.
2. Reverify mutable board/system facts through read-only SSH commands.
3. Create compatibility, runbook, ADR, and task report documents.
4. Update stable context and handoff.
5. Validate links, secrets, commands, and Markdown consistency.

## Installed or changed packages

None.

## Created or changed files

| Path | Change | Purpose | Owner/mode | Rollback |
|---|---|---|---|---|
| `/home/artm1904/Program/Robot/robotics-lab-workspace/docs/agent-context/STEPPER_MOTOR_COMPATIBILITY.md` | Created | Compatibility baseline | current user | Delete file |
| `/home/artm1904/Program/Robot/robotics-lab-workspace/docs/runbooks/ULN2003_STEPPER_MOTOR.md` | Created | Safe staged operation | current user | Delete file |
| `/home/artm1904/Program/Robot/robotics-lab-workspace/docs/decisions/ADR-0004-STEPPER-LIBGPIOD-COMPATIBILITY.md` | Created | Durable API/mapping decision | current user | Delete file |
| `/home/artm1904/Program/Robot/robotics-lab-workspace/docs/worklog/2026-09-08-STEPPER-DOCUMENTATION-AND-COMPATIBILITY.md` | Created | Task evidence | current user | Delete file |
| `/home/artm1904/Program/Robot/robotics-lab-workspace/docs/agent-context/ENVIRONMENT.md` | Updated | Current compatibility facts | current user | Revert edit |
| `/home/artm1904/Program/Robot/robotics-lab-workspace/docs/handoffs/CURRENT.md` | Updated | Current motor continuation state | current user | Revert edit |
| `/home/artm1904/Program/Robot/robotics-lab-workspace/docs/README.md` | Updated | Motor documentation index | current user | Revert edit |
| `/home/artm1904/Program/Robot/robotics-lab-workspace/docs/decisions/README.md` | Updated | ADR-0004 index entry | current user | Revert edit |
| `/home/artm1904/Program/Robot/robotics-lab-workspace/stepper-motor/README.md` | Updated in submodule | Correct operating reference | current user | Revert edit |

## Commands executed

Local workstation, canonical workspace:

```bash
sed -n ... AGENTS.md docs/... stepper-motor/README.md
rg --files docs stepper-motor
```

Purpose: read all required instructions and only task-relevant history.

Result: documentation ownership, workflow, safety, and reporting requirements
were identified.

Orange Pi, read-only over SSH:

```bash
uname -r
cat /etc/os-release
uname -m
python3 --version
python3 -c 'import gpiod; print(gpiod.__version__)'
sha256sum /root/stepper-motor/stepper_cli.py
gpioinfo gpiochip0 | grep -E 'line +(38|99|100|141):'
grep -E 'pin (38|99|100|141) ' \
  /sys/kernel/debug/pinctrl/2000000.pinctrl/pinmux-pins
```

Purpose: reverify mutable compatibility facts without requesting GPIOs.

Result: expected system versions and deployed script checksum observed; all
four GPIOs were unused and pinctrl-unclaimed. Commands exited 0.

## Experiments

### EXP-DOC-001: Compatibility revalidation

- Hypothesis: the recorded August compatibility facts still describe the live
  board on 2026-09-08.
- Changed variable: none; read-only inspection.
- Procedure: query OS, kernel, architecture, Python/gpiod, script checksum,
  gpioinfo, and pinctrl debugfs.
- Measurements: kernel 6.6.98; Python 3.12.3; gpiod 1.6.3; four lines unused and
  unclaimed; deployed script SHA-256 begins `640b16ab`.
- Result: passed.
- Interpretation: current documentation can retain the verified compatibility
  baseline while marking powered rotation unverified.
- Next experiment: bounded 8-half-step powered motion under direct observation.

## Errors and diagnosis

- Package-version formatting in one read-only SSH query expanded a dpkg format
  token in the remote shell, producing empty labels. Direct Python import and
  prior package evidence still established gpiod 1.6.3; no system state changed.
- The legacy `/home/artm1904/Program/Robot/os` path was initially treated as
  active. The user corrected the workspace location, so deliverables were
  adapted to the canonical superproject and its submodule boundaries.

## Rejected hypotheses

- **Rejected:** Python gpiod is absent. It imports successfully as version 1.6.3.
- **Rejected:** kernel line names can identify the four pins. The live gpiochip
  reports them as unnamed; offsets plus pinctrl evidence are required.

## Validation

Canonical workspace:

```bash
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s stepper-motor -v
git diff --check
git -C stepper-motor diff --check
rg -n '/home/artm1904/Program/Robot/os|--lines|SSH password|1904' <changed-files>
test -e <each-new-relative-link-target>
```

Three tests passed in 0.002 seconds. Both diff checks passed. The focused scan
found only intentional historical/canonical path discussion and the statement
that `--lines` was removed; no credential value was found. Every new relative
Markdown target exists.

## Final result

Compatibility note, operating runbook, ADR, and updated repository context were
created in the canonical superproject; the stepper README was corrected in its
submodule. No powered motor test or target mutation occurred.

## Limitations and open questions

- Powered right/left movement remains unverified.
- Exact motor model, phase current, gearbox ratio, load, and measured
  steps-per-output-revolution remain unknown.
- Header-pin mapping must be rechecked physically after wiring changes.

## Reproduction from a clean state

Follow `docs/runbooks/ULN2003_STEPPER_MOTOR.md` from Stage 1 onward.

## Rollback

Revert or remove the documentation files listed above. No target rollback is
needed because the board was inspected read-only.

## Next steps

Perform and record the bounded powered-motion stage only with the hardware in
view and an immediate power-disconnect path.

## Learning topics

- libgpiod v1 versus v2 Python APIs
- Allwinner GPIO bank-to-offset mapping
- ULN2003 current sinking and flyback protection
- Linux scheduling jitter in step generation

## Sources

- Repository `AGENTS.md`, environment, workflow, prior motor worklog, and source
- Live Orange Pi OS, gpioinfo, and pinctrl debugfs observations on 2026-09-08
