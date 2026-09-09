# ADR-0004: Use libgpiod Character Devices with Dual Python API Support

- Date: 2026-09-08
- Status: Accepted

## Context

The Orange Pi Zero 3W runs an Ubuntu Noble-based Armbian image whose repository
ships Python libgpiod 1.6.3. The initial controller assumed libgpiod 2.x and
failed during import of the 2.x-only `gpiod.line` module. The vendor kernel
exposes PE13, PD3, PB6, and PD4 as unnamed gpiochip0 lines, so line-name lookup
is unavailable even though pinctrl identifies the SoC pins.

## Decision

- Use the Linux GPIO character-device interface, not deprecated sysfs GPIO or
  direct register access.
- Keep one controller with runtime selection between libgpiod 1.6 and 2.x
  Python APIs.
- Address the four outputs as verified `/dev/gpiochip0` offsets
  `141 99 38 100` in ULN2003 IN1–IN4 order.
- Request all four lines together, initialize inactive, and write all inactive
  during shutdown.
- Retain the distribution `python3-libgpiod` package on the board.

## Consequences

- The current Armbian image works without replacing system Python packages.
- The code remains portable to a future libgpiod 2.x image.
- Offsets are kernel/controller-specific and must be reverified after board,
  kernel, or Device Tree changes.
- Userspace timing is non-real-time and unsuitable for precision motion.

## Alternatives rejected

- Require libgpiod 2.x from pip: conflicts with the distribution baseline and
  adds an unnecessary package-management path.
- Use GPIO sysfs: deprecated and provides weaker multi-line request semantics.
- Write pinctrl/GPIO registers directly: unsafe ownership conflicts and poor
  portability.
- Resolve by GPIO line names: the live kernel reports the lines as unnamed.

## Validation

Local unit tests and dry-run passed. On the live board, the libgpiod 1.6 backend
requested all four offsets inactive and released them successfully without a
motion command. Powered rotation remains a separate experiment.
