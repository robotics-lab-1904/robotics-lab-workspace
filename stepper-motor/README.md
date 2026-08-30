# ULN2003 stepper motor CLI

This tool drives a four-phase unipolar stepper through a ULN2003 using the
Linux GPIO character-device API. It supports the libgpiod 1.6 API shipped on
the board and the newer 2.x API. Its default mapping is:

| Header pin | SoC line | gpiochip0 offset | ULN2003 |
|---:|---|---:|---|
| 31 | PE13 | 141 | IN1 |
| 33 | PD3 | 99 | IN2 |
| 35 | PB6 | 38 | IN3 |
| 37 | PD4 | 100 | IN4 |

The SoC names and offsets were verified live on this Orange Pi: all four lines
belong to `/dev/gpiochip0`, are unused, and are unclaimed by pinctrl. The
header-pin mapping still originates from the user's wiring/pinout. The Orange
Pi and ULN2003 logic side must share ground. Never connect the motor supply to
a GPIO pin.

## Install and verify on the Orange Pi

Power down before changing wiring. After checking connector orientation,
pinout, 5 V output, and common ground, power up and run:

```bash
sudo apt update
sudo apt install gpiod python3-libgpiod
gpioinfo gpiochip0 | grep -E 'line +(38|99|100|141):'
python3 -c 'import gpiod; print(gpiod.__version__)'
```

First test without hardware access:

```bash
cd /path/to/stepper-motor
python3 stepper_cli.py --dry-run
```

Then make a very small powered test:

```bash
sudo python3 stepper_cli.py --steps 8 --delay-ms 5
```

At the prompt, `r` moves right, `l` moves left, an optional number overrides
the half-step count (`r 32`), `off` de-energizes all coils, and `q` exits.
Increase the move gradually only after confirming the expected direction and
that the motor and driver remain cool.

The default releases the coils after each move to reduce heating. `--hold`
keeps holding torque but also keeps coils energized. “Right” and “left” depend
on motor wiring; if reversed, swap the command or reverse `--lines`.
