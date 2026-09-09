# Stepper Powered-Motion Validation

- Date: 2026-09-08
- Status: Completed (user-observed functional test)
- Owner/agent: User with Codex documentation
- Related issue/task: Validate physical Orange Pi–ULN2003–motor integration

## Objective

Record the first successful powered movement of the stepper motor using the
documented Orange Pi GPIO mapping, ULN2003 board, and Python controller.

## Success criteria

- Physical wiring is complete.
- The controller starts successfully on the Orange Pi.
- The connected stepper produces correct rotation rather than only vibration.

## Environment

### Local workstation

- Canonical documentation workspace:
  `/home/artm1904/Program/Robot/robotics-lab-workspace`

### Target hardware

- Orange Pi Zero 3W
- ULN2003 driver board
- Four-phase stepper motor; exact model not recorded
- Separately regulated 5 V motor supply; measured load voltage not recorded
- GPIO mapping: PE13/PD3/PB6/PD4 to ULN2003 IN1/IN2/IN3/IN4

### Software versions

- Previously verified kernel: `6.6.98-vendor-sun60iw2`
- Previously verified Python: 3.12.3
- Previously verified Python gpiod: 1.6.3
- Controller: `/root/stepper-motor/stepper_cli.py`

## Initial state

GPIO offsets, ownership, API compatibility, local sequence tests, dry-run, and
live zero-motion request/release had passed. Physical powered movement remained
unverified in the documentation.

## Safety and rollback plan

The user physically connected the system. The established rollback is to stop
the CLI with `q` or Ctrl-C, disconnect motor power, and power down before any
wiring change. Stop immediately on heat, smell, unstable power, or resets.

## Theory and references

Successful rotation exercises the complete functional path: Python half-step
sequence → Linux GPIO → ULN2003 inputs/current sinks → motor phases → rotor.

## Plan

1. Complete physical wiring.
2. Run the controller on the Orange Pi.
3. Observe whether the motor rotates correctly.
4. Record the outcome and remaining unmeasured limits.

## Installed or changed packages

None reported during this validation.

## Created or changed files

| Path | Change | Purpose | Owner/mode | Rollback |
|---|---|---|---|---|
| `docs/worklog/2026-09-08-STEPPER-POWERED-MOTION-VALIDATION.md` | Created | Record physical validation | current user | Delete file |
| `docs/agent-context/STEPPER_MOTOR_COMPATIBILITY.md` | Updated | Mark powered compatibility | current user | Revert edit |
| `docs/runbooks/ULN2003_STEPPER_MOTOR.md` | Updated | Mark Stage 4 complete | current user | Revert edit |
| `docs/agent-context/ENVIRONMENT.md` | Updated | Record subsystem status | current user | Revert edit |
| `docs/handoffs/CURRENT.md` | Updated | Move next work to characterization | current user | Revert edit |
| `stepper-motor/README.md` | Updated in submodule | Expose validation status | current user | Revert edit |

## Commands executed

**User-reported:** the Python controller was run on the Orange Pi after physical
wiring was completed. The exact command line, CLI commands, and exit status
were not captured, so no more specific command is asserted here.

## Experiments

### EXP-MOTOR-002: First powered rotation

- Hypothesis: the verified GPIO mapping and half-step sequence will drive the
  physically connected motor through the ULN2003.
- Changed variable: motor power and completed physical signal wiring were
  present for the movement test.
- Procedure: run the program and observe the motor.
- Measurements: qualitative observation only; no electrical, timing, thermal,
  or displacement measurements recorded.
- Result: **Passed — user-observed.** The program worked and the stepper motor
  rotated correctly.
- Interpretation: GPIO order, ULN2003 connection, motor phase sequence, and
  basic power path are functionally compatible in the tested assembly.
- Next experiment: bounded, measured characterization under a documented load.

## Errors and diagnosis

No error was reported for the powered movement test.

## Rejected hypotheses

- **Rejected for this assembly:** the documented phase order necessarily causes
  vibration without rotation. Correct rotation was observed.
- **Rejected for this assembly:** the controller cannot operate with the
  board's installed libgpiod 1.6.3. End-to-end movement succeeded.

## Validation

Evidence is the user's direct physical observation. Codex did not independently
observe the motor, capture terminal output, or collect instrument readings.

## Final result

The Orange Pi Zero 3W, documented GPIO offsets, ULN2003 board, physical wiring,
and stepper controller are functionally compatible for powered rotation.

## Limitations and open questions

- Exact `r`/`l` commands, half-step count, delay, and exit status were not saved.
- Correct operation in both directions was not separately recorded.
- Motor model, supply current/voltage under load, temperature, torque/load,
  steps per output revolution, reliable speed range, and duration are unknown.
- No sustained-load or restart/reboot test has been performed.

## Reproduction from a clean state

Follow `docs/runbooks/ULN2003_STEPPER_MOTOR.md` through Stage 4 and record exact
commands and measurements for the next run.

## Rollback

Exit with `q` or Ctrl-C, disconnect motor power, and power down before changing
wiring. Software rollback is not required for this successful validation.

## Next steps

Run a measured Stage 5 experiment: document motor model and load; test both
directions; measure steps per revolution, voltage/current, temperature, and the
reliable delay range; then perform a bounded sustained run.

## Learning topics

- Stepper phase order and half-step commutation
- Missed-step and stall detection
- Motor/driver thermal limits
- Gearbox ratio and output-shaft calibration

## Sources

- User report on 2026-09-08
- `docs/agent-context/STEPPER_MOTOR_COMPATIBILITY.md`
- `docs/runbooks/ULN2003_STEPPER_MOTOR.md`
- `docs/worklog/2026-08-29-ULN2003-STEPPER-CLI.md`
