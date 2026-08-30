#!/usr/bin/env python3
"""Interactive four-phase stepper controller using Linux GPIO character devices."""

from __future__ import annotations

import argparse
import shlex
import signal
import sys
import time
from dataclasses import dataclass
from typing import Protocol, Sequence


HALF_STEP_SEQUENCE: tuple[tuple[int, int, int, int], ...] = (
    (1, 0, 0, 0),
    (1, 1, 0, 0),
    (0, 1, 0, 0),
    (0, 1, 1, 0),
    (0, 0, 1, 0),
    (0, 0, 1, 1),
    (0, 0, 0, 1),
    (1, 0, 0, 1),
)


class Outputs(Protocol):
    def write(self, values: Sequence[int]) -> None: ...

    def close(self) -> None: ...


class DryRunOutputs:
    def __init__(self, *, trace: bool = False) -> None:
        self.trace = trace
        self.writes: list[tuple[int, ...]] = []

    def write(self, values: Sequence[int]) -> None:
        state = tuple(values)
        self.writes.append(state)
        if self.trace:
            print("GPIO", "".join(map(str, state)))

    def close(self) -> None:
        pass


class GpiodOutputs:
    """Output request compatible with libgpiod Python APIs 1.6 and 2.x."""

    def __init__(self, chip_path: str, offsets: Sequence[int]) -> None:
        try:
            import gpiod
        except (ImportError, ModuleNotFoundError) as error:
            raise RuntimeError(
                "Python libgpiod is required (on Armbian: apt install python3-libgpiod)"
            ) from error

        self._gpiod = gpiod
        self._offsets = tuple(offsets)
        try:
            if hasattr(gpiod, "request_lines"):
                from gpiod.line import Direction, Value

                self._Value = Value
                settings = gpiod.LineSettings(
                    direction=Direction.OUTPUT, output_value=Value.INACTIVE
                )
                self._request = gpiod.request_lines(
                    chip_path,
                    consumer="stepper-cli",
                    config={self._offsets: settings},
                )
                self._api_version = 2
            else:
                self._chip = gpiod.Chip(chip_path)
                self._request = self._chip.get_lines(self._offsets)
                self._request.request(
                    consumer="stepper-cli",
                    type=gpiod.LINE_REQ_DIR_OUT,
                    default_vals=[0, 0, 0, 0],
                )
                self._api_version = 1
        except (OSError, TypeError, AttributeError) as error:
            raise RuntimeError(
                f"cannot request GPIO offsets {self._offsets} on {chip_path}: {error}"
            ) from error

    def write(self, values: Sequence[int]) -> None:
        if self._api_version == 2:
            mapped = {
                offset: self._Value.ACTIVE if value else self._Value.INACTIVE
                for offset, value in zip(self._offsets, values, strict=True)
            }
            self._request.set_values(mapped)
        else:
            self._request.set_values(list(values))

    def close(self) -> None:
        self._request.release()
        if self._api_version == 1:
            self._chip.close()


@dataclass
class Stepper:
    outputs: Outputs
    delay_seconds: float
    release_after_move: bool = True
    sequence_index: int = 0

    def move(self, signed_steps: int) -> None:
        direction = 1 if signed_steps >= 0 else -1
        for _ in range(abs(signed_steps)):
            self.outputs.write(HALF_STEP_SEQUENCE[self.sequence_index])
            time.sleep(self.delay_seconds)
            self.sequence_index = (self.sequence_index + direction) % len(HALF_STEP_SEQUENCE)
        if self.release_after_move:
            self.release()

    def release(self) -> None:
        self.outputs.write((0, 0, 0, 0))

    def close(self) -> None:
        self.release()
        self.outputs.close()


def parse_command(text: str, default_steps: int) -> int | None:
    fields = shlex.split(text.lower())
    if not fields:
        return 0
    if fields[0] in {"q", "quit", "exit"}:
        return None
    if fields[0] in {"r", "right", "l", "left"}:
        if len(fields) > 2:
            raise ValueError("use: r [half-steps] or l [half-steps]")
        steps = default_steps if len(fields) == 1 else int(fields[1])
        if steps <= 0:
            raise ValueError("half-steps must be greater than zero")
        return steps if fields[0] in {"r", "right"} else -steps
    if fields[0] in {"off", "release"}:
        return 0
    raise ValueError("commands: r [steps], l [steps], off, q")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Control a 4-phase stepper through a ULN2003")
    parser.add_argument("--chip", default="/dev/gpiochip0", help="GPIO character device")
    parser.add_argument(
        "--offsets",
        nargs=4,
        type=int,
        default=(141, 99, 38, 100),
        metavar="N",
        help="IN1..IN4 line offsets (default: PE13 PD3 PB6 PD4)",
    )
    parser.add_argument("--steps", type=int, default=128, help="default half-steps per command")
    parser.add_argument("--delay-ms", type=float, default=3.0, help="delay between half-steps")
    parser.add_argument("--hold", action="store_true", help="keep coils energized after a move")
    parser.add_argument("--dry-run", action="store_true", help="do not access GPIO")
    parser.add_argument("--trace", action="store_true", help="print states (useful with --dry-run)")
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    if args.steps <= 0 or args.delay_ms <= 0:
        print("error: --steps and --delay-ms must be greater than zero", file=sys.stderr)
        return 2
    try:
        outputs: Outputs = (
            DryRunOutputs(trace=args.trace)
            if args.dry_run
            else GpiodOutputs(args.chip, args.offsets)
        )
    except RuntimeError as error:
        print(f"error: {error}", file=sys.stderr)
        return 1

    motor = Stepper(outputs, args.delay_ms / 1000.0, release_after_move=not args.hold)

    def request_stop(_signum: int, _frame: object) -> None:
        raise KeyboardInterrupt

    signal.signal(signal.SIGINT, request_stop)
    signal.signal(signal.SIGTERM, request_stop)
    labels = ("PE13", "PD3", "PB6", "PD4")
    mapping = ", ".join(
        f"{label}={offset}" for label, offset in zip(labels, args.offsets, strict=True)
    )
    print(f"Lines IN1..IN4 on {args.chip}: {mapping}; default: {args.steps} half-steps")
    print("Commands: r [steps], l [steps], off, q")
    try:
        while True:
            try:
                command = input("stepper> ")
                movement = parse_command(command, args.steps)
            except EOFError:
                break
            except (ValueError, TypeError) as error:
                print(f"error: {error}")
                continue
            if movement is None:
                break
            if movement == 0:
                motor.release()
            else:
                motor.move(movement)
                print(f"moved {abs(movement)} half-steps {'right' if movement > 0 else 'left'}")
    except KeyboardInterrupt:
        print("\nstopping; coils released")
    finally:
        motor.close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
