# ULN2003 Stepper Motor on Orange Pi Zero 3W

## Purpose

Safely verify and operate the four-phase stepper connected through the ULN2003
board. This runbook is validated through detection, dry-run, and live
zero-motion GPIO request/release. The user confirmed successful powered
rotation on 2026-09-08; exact motion parameters and measurements were not
captured.

## Preconditions

- Power off before touching GPIO, motor, driver, or regulator wiring.
- Confirm header orientation and the mapping in
  `docs/agent-context/STEPPER_MOTOR_COMPATIBILITY.md`.
- Measure approximately 5.0 V at the LM2596 output before connecting it.
- Connect Orange Pi GND to ULN2003 GND. Do not power the motor from a GPIO.
- Ensure the motor shaft/load can move safely in both directions.
- Stop on heating, smell, unstable power, resets, or disappearing indicators.

## Stage 1: detect the system

Run on the Orange Pi:

```bash
uname -a
cat /etc/os-release
python3 --version
python3 -c 'import gpiod; print(gpiod.__version__)'
gpioinfo gpiochip0 | grep -E 'line +(38|99|100|141):'
```

Expected for the verified image: Python 3.12.3, gpiod 1.6.3, and all four lines
with no consumer. Stop if any line is `[used]` or has an unexpected consumer.

If the Python import fails:

```bash
apt update
apt install gpiod python3-libgpiod
```

Do not replace the distribution package with an unrelated `pip` package unless
the compatibility decision is deliberately revisited.

## Stage 2: software-only validation

```bash
cd /root/stepper-motor
python3 stepper_cli.py --dry-run
```

Enter `r 2`, `l 2`, `off`, then `q`. Add `--trace` to display coil states.
Dry-run never opens a gpiochip and cannot validate physical wiring.

## Stage 3: live zero-motion request

```bash
cd /root/stepper-motor
printf 'q\n' | python3 stepper_cli.py --steps 8 --delay-ms 5
```

Expected: the prompt appears and the process exits 0 without moving. This stage
requests the four GPIOs as inactive outputs and releases them immediately.

## Stage 4: bounded powered movement

This stage was completed successfully by the user on 2026-09-08: the connected
motor rotated correctly. Repeat it with the motor visible and within immediate
power-disconnect reach whenever wiring, motor, driver, kernel, or GPIO mapping
changes.

```bash
cd /root/stepper-motor
python3 stepper_cli.py --steps 8 --delay-ms 5
```

At `stepper>` enter one command:

```text
r
```

Observe motion, sound, supply stability, and temperature. Then test the inverse:

```text
l
```

The words “right” and “left” are conventional: external coil order and viewing
direction determine physical rotation. If movement is rough or only vibrates,
stop with `q` and verify IN1–IN4 order rather than increasing current or speed.

## Stage 5: increase only after success

Increase one variable at a time, for example `r 32`, then `r 128`. Retain the
5 ms delay until motion is reliable. Reduce delay gradually only under a known
load while watching for missed steps or stalls.

For a typical geared motor, do not assume a steps-per-revolution value; gearbox
ratios and manufacturing variants differ. Measure the output shaft and record
the result in the worklog.

Stage 5 remains unverified: no sustained-load, thermal, current, speed-limit,
missed-step, or steps-per-revolution measurements have been recorded.

## Commands

| Command | Effect |
|---|---|
| `r` / `right` | Default half-steps in positive sequence order |
| `l` / `left` | Default half-steps in reverse sequence order |
| `r 32` / `l 32` | Move exactly 32 half-steps |
| `off` | Write all four outputs inactive |
| `q` | Release coils and exit |

Options:

```text
--steps N       default half-steps per r/l command
--delay-ms MS   delay between half-steps
--hold          retain coil holding torque after movement; increases heating
--dry-run       do not access GPIO
--trace         print states in dry-run mode
--chip PATH     override /dev/gpiochip0
--offsets A B C D  override IN1..IN4 offsets
```

## Failure handling

- `Python libgpiod is required`: install `python3-libgpiod` and verify the
  interpreter is `/usr/bin/python3`.
- `Device or resource busy`: another consumer owns at least one line; do not
  force it. Inspect `gpioinfo gpiochip0`.
- Vibration without rotation: likely phase order, insufficient voltage under
  load, too-fast stepping, mechanical load, or incompatible motor wiring.
- Reversed direction: use the opposite command; direction names are relative.
- Reset or SSH loss: disconnect motor power, retain Orange Pi power if safe,
  then inspect the persistent journal and power path.

## Shutdown and rollback

Use `q` or Ctrl-C. The program writes `0000` in its shutdown path. To restore
the pre-compatibility script on the SBC:

```bash
cp -a /root/stepper-motor/stepper_cli.py.before-libgpiod1-20260829 \
  /root/stepper-motor/stepper_cli.py
```

Rollback restores software only; power off before reverting wiring.
