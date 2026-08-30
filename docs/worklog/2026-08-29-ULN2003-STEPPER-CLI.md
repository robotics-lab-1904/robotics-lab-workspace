# ULN2003 Stepper Motor CLI

> Historical path notice (2026-08-30): this report records work performed in
> `/home/artm1904/Program/Robot/os`. The maintained local source is now the
> `stepper-motor/` submodule of
> `/home/artm1904/Program/Robot/robotics-lab-workspace`.

- Date: 2026-08-29
- Status: GPIO request/release validated; powered motion pending
- Owner/agent: Codex
- Related issue/task: Interactive right/left motor control

## Objective

Create a bounded interactive CLI for a four-phase stepper connected to an
Orange Pi Zero 3W through a ULN2003 board.

## Success criteria

- Accept `r` and `l`, with an optional half-step count.
- Drive a correct eight-state half-step sequence through Linux GPIO.
- De-energize all coils on normal exit, signals, and by default after moves.
- Provide a dry-run path and unit tests.
- Do not claim hardware success until the live GPIO mapping is verified.

## Environment

### Local workstation

- Workspace: `/home/artm1904/Program/Robot/os`
- Python: 3.14.7

### Target hardware

- Documented board: Orange Pi Zero 3W, Allwinner sun60iw2
- Reported wiring: PE13/PD3/PB6/PD4 to ULN2003 IN1/IN2/IN3/IN4
- Motor supply: separately regulated 5.0 V

### Software versions

- Target kernel documented as `6.6.98-vendor-sun60iw2`; live value unverified.
- Live target has `gpiod` and `python3-libgpiod` 1.6.3-1.1build1.

## Initial state

No motor-control source or runbook existed in the workspace. SSH key
authentication was initially unavailable but was configured by the user later;
the live gpiochips, packages, and pinctrl state were then inspected.

## Safety and rollback plan

Power down before wiring changes. Verify pinout, ground, regulator output, and
connector orientation. Start with 8 half-steps at 5 ms. The program requests
GPIO lines inactive and releases them on exit. Rollback is removal of the new
`stepper-motor/` directory; no target files or services have been changed.

## Theory and references

The ULN2003 sinks motor coil current; Orange Pi GPIO drives only its logic
inputs. An eight-state half-step sequence alternates one and two energized
phases. Reversing traversal reverses rotation.

## Plan

1. Implement gpiochip/offset-based libgpiod output control and dry-run backend.
2. Add parser/sequence tests.
3. Validate locally without GPIO.
4. Verify and deploy on the live board in a later hardware session.

## Installed or changed packages

None.

## Created or changed files

| Path | Change | Purpose | Owner/mode | Rollback |
|---|---|---|---|---|
| `/home/artm1904/Program/Robot/os/stepper-motor/stepper_cli.py` | Created | CLI/controller | current user | Delete file |
| `/home/artm1904/Program/Robot/os/stepper-motor/test_stepper_cli.py` | Created | Unit tests | current user | Delete file |
| `/home/artm1904/Program/Robot/os/stepper-motor/README.md` | Created | Safety and operation guide | current user | Delete file |
| `/home/artm1904/Program/Robot/os/docs/worklog/2026-08-29-ULN2003-STEPPER-CLI.md` | Created | Evidence/report | current user | Delete file |
| `/root/stepper-motor/stepper_cli.py` | Updated on board | libgpiod 1.6-compatible controller | root:root 0644 | Restore `.before-libgpiod1-20260829` backup |

## Commands executed

Workstation, `/home/artm1904/Program/Robot/os`:

```bash
rg --files ...
rg -n -i 'gpio|stepper|motor|orange pi|uln2003|libgpiod|wiring' ...
ssh -F /dev/null -o BatchMode=yes -o ConnectTimeout=5 root@<BOARD> ...
```

Purpose: inspect required context, existing implementation, and target state.

Result: repository context inspected; no motor implementation found; SSH was
rejected because unattended credentials were unavailable.

Target board, `/root/stepper-motor`:

```bash
dpkg -l gpiod python3-libgpiod
gpioinfo gpiochip0
grep -E 'pin (38|99|100|141) ' /sys/kernel/debug/pinctrl/2000000.pinctrl/pinmux-pins
printf 'q\n' | python3 stepper_cli.py --steps 8 --delay-ms 5
```

Purpose: verify package/API version, offsets, ownership, and a zero-motion GPIO
request/release.

Result: libgpiod 1.6.3 was installed; offsets 38, 99, 100, and 141 were unused
and unclaimed. The updated tool requested all four, initialized them inactive,
accepted `q`, wrote all inactive, released the request, and exited 0. No motor
step was commanded. After release, libgpiod 1.6 left direction as output while
the lines had no consumer; the tool's final commanded values were inactive.

## Experiments

### EXP-MOTOR-001: Local sequence and CLI validation

- Hypothesis: dry-run and unit tests can validate direction traversal, parsing,
  bounds, and coil release without energizing hardware.
- Changed variable: none on target hardware.
- Procedure: compile both Python files; run unittest discovery; pipe `r 2`,
  `l 2`, `off`, and `q` into the traced dry-run CLI.
- Measurements: 3 tests ran in 0.001 seconds; process exit status 0.
- Result: passed. Trace showed forward states `1000`, `1100`, release;
  reverse states `0100`, `1100`, release; `off` and exit also released.
- Interpretation: command parsing, sequence traversal, and the no-hardware backend
  behave as designed. This does not validate the target libgpiod API or wiring.
- Next experiment: live line-name and minimal powered-motion validation.

## Errors and diagnosis

- Default workstation SSH configuration had invalid ownership/permissions.
  Using an empty SSH configuration reached the board, but authentication was
  initially rejected. The user subsequently configured key authentication.
- Ubuntu Noble installed Python libgpiod 1.6.3, not the 2.x API assumed by the
  original code. The error handler incorrectly described this as a missing
  module. The backend now detects and supports both APIs.

## Rejected hypotheses

None.

## Validation

On the local workstation:

```bash
python3 -m py_compile stepper-motor/stepper_cli.py stepper-motor/test_stepper_cli.py
python3 -m unittest discover -s stepper-motor -v
printf 'r 2\nl 2\noff\nq\n' | python3 stepper-motor/stepper_cli.py \
  --dry-run --trace --delay-ms 0.01
```

All commands exited 0. Three tests passed. Hardware GPIO was not accessed.

## Final result

Interactive CLI, dry-run backend, tests, and operating guide completed and
locally validated. The corrected script was deployed to the board and a
zero-motion GPIO request/release passed. No package or service was changed and
no powered movement was commanded.

## Limitations and open questions

- The live kernel exposes the lines without names. Pinctrl verified the mapping
  on gpiochip0 as PE13=141, PD3=99, PB6=38, and PD4=100; all are unclaimed and
  reported unused. Physical header placement still depends on the board pinout.
- Exact motor model, steps per output-shaft revolution, safe maximum speed, and
  load are unknown.
- Direction labels are conventional and may be reversed by coil order.

## Reproduction from a clean state

See `/home/artm1904/Program/Robot/os/stepper-motor/README.md`.

## Rollback

Exit the program to release GPIOs. Remove the created files if no longer needed.

## Next steps

After the user verifies common ground, regulator voltage, and safe mechanics,
perform an 8-half-step/5-ms powered test.

## Learning topics

- Unipolar stepper half-step sequencing
- ULN2003 Darlington voltage drop and flyback paths
- Linux GPIO character-device ownership and line naming

## Sources

- Repository environment and workflow documents
- Official libgpiod 2.3 Python API: `request_lines`, `LineSettings`, and
  `LineRequest.set_values`: https://libgpiod.readthedocs.io/en/v2.3/python_api.html
