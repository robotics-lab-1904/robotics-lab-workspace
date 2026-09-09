# ULN2003 Stepper Motor Compatibility

Last verified: 2026-09-08

## Scope

This note defines the known compatibility of `stepper-motor/stepper_cli.py`
with the lab Orange Pi Zero 3W. It separates live observations from wiring and
motor properties that have not yet been measured.

## Compatibility matrix

| Layer | Board/system value | Controller compatibility | Evidence |
|---|---|---|---|
| Board | Orange Pi Zero 3W, Allwinner `sun60iw2` | Compatible | Live host identity and repository environment |
| Architecture | AArch64 | Compatible | `uname -m` returned `aarch64` |
| OS | Armbian-unofficial 26.08.0-trunk, Ubuntu Noble | Compatible | Live `/etc/os-release` |
| Kernel | `6.6.98-vendor-sun60iw2` | Compatible with GPIO character device | Live `uname -r` and `/dev/gpiochip0` |
| Python | 3.12.3 | Compatible | Live `python3 --version`; local tests cover 3.14.7 |
| Python gpiod | 1.6.3 | Compatible | Live import and zero-motion request/release |
| libgpiod 2.x Python API | Not installed on this SBC | Supported by code, not tested on this SBC | Separate backend selected when `gpiod.request_lines` exists |
| GPIO controller | `/dev/gpiochip0`, 352 lines | Compatible | Live `gpioinfo` |
| Required offsets | 141, 99, 38, 100 | Available | Live gpioinfo and pinctrl debugfs |
| Pin ownership | Unclaimed; no active consumer | Available for controller | Live pinctrl and gpioinfo on 2026-09-08 |
| Powered rotation | Connected motor and ULN2003 | Compatible | User reported correct physical rotation on 2026-09-08 |

## GPIO mapping

Allwinner main-controller offsets use the bank position in the controller:
`PB6=38`, `PD3=99`, `PD4=100`, and `PE13=141`. This kernel exposes these
gpiochip lines as `unnamed`, so line-name discovery is not usable.

| Sequence order | Header pin | SoC pin | gpiochip0 offset | ULN2003 input |
|---:|---:|---|---:|---|
| 1 | 31 | PE13 | 141 | IN1 |
| 2 | 33 | PD3 | 99 | IN2 |
| 3 | 35 | PB6 | 38 | IN3 |
| 4 | 37 | PD4 | 100 | IN4 |

The SoC pin-to-offset relationship was observed live. The header position and
ULN2003 connection were physically assembled and functionally validated by the
user through successful powered rotation. They must still be visually checked
whenever wiring changes.

## API compatibility mechanism

The controller detects the Python binding generation at runtime:

- libgpiod 2.x: `gpiod.request_lines`, `LineSettings`, and `Value`;
- libgpiod 1.6: `Chip.get_lines`, `LINE_REQ_DIR_OUT`, and bulk `set_values`.

Both backends request all four lines together and initialize them inactive.
The controller writes `0000` after a move by default and again during shutdown.
With libgpiod 1.6, releasing a request can leave the pins configured as outputs;
they have no consumer after exit, and the last controller write is inactive.

## Electrical compatibility boundaries

- Orange Pi GPIO signals are logic controls only; motor current flows through
  the ULN2003 and separate 5 V motor supply.
- Orange Pi ground and ULN2003 ground must be common.
- The exact motor model, winding current, gearbox ratio, torque/load, and safe
  maximum stepping rate have not been recorded.
- The LM2596 output must be measured before connection; its dial position is
  not evidence of 5.0 V output.
- `--hold` increases heat because it leaves one or two coils energized.

## Powered validation status

**User-observed:** on 2026-09-08, after completing the physical connections,
the controller ran and the stepper motor rotated correctly. This validates the
end-to-end path from GPIO sequence through ULN2003 to the motor for that wiring.

The exact command, direction commands exercised, number of half-steps, supply
voltage under load, current, temperature, load, and duration were not captured.
The result is therefore functional compatibility evidence, not a quantified
reliability or performance test.

## Known limitation

Linux userspace scheduling does not provide hard real-time step timing. This
CLI is suitable for bounded manual experiments, not precise motion control or
high-rate coordinated axes. A timer-driven kernel/peripheral solution or MCU
is preferable if timing jitter becomes functionally important.

## Verification commands

Run on the Orange Pi:

```bash
uname -r
python3 --version
python3 -c 'import gpiod; print(gpiod.__version__)'
gpioinfo gpiochip0 | grep -E 'line +(38|99|100|141):'
grep -E 'pin (38|99|100|141) ' \
  /sys/kernel/debug/pinctrl/2000000.pinctrl/pinmux-pins
```

Interpretation:

- `[used]` or a named consumer means stop and identify the owner first.
- `UNCLAIMED` in pinctrl and `unused` in gpioinfo mean no current owner was
  observed; they do not prove the external wiring is correct.
