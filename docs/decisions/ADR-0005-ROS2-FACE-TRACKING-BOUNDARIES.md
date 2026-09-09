# ADR-0005: Reuse camera ownership and bound ROS 2 stepper commands

- Status: Accepted
- Date: 2026-09-09
- Supersedes: None

## Context

Chapter 2's USB camera and Dynamixel servo examples do not match the lab's
vendor OV5647 pipeline and ULN2003 stepper. Camera buffer count and process
lifetime have existing constraints. The stepper has no measured shaft feedback
or homing and its mounting/calibration are unknown.

## Decision

- Keep the existing single-client MJPEG server as camera owner. The initial
  ROS camera bridge consumes its HTTP stream and never opens the V4L2 device.
- Use distribution OpenCV Haar detection as a baseline. Publish one largest
  face with normalized coordinates and explicit absence, stamped from its image.
- Use an explicit `StepperCommand` message in signed half-steps per second;
  do not present uncalibrated counts as radians or measured joint states.
- Preserve originating image timestamps through the control path; reject stale
  or significantly future-dated commands. Also use a monotonic local watchdog.
- Start every motor node disarmed and default to dry-run. Request GPIO only on
  explicit enable; initialize inactive and release on disable/shutdown/fault.
- Bound estimated travel and total steps per process. Re-enable must not reset
  those counters. Never emit catch-up bursts after scheduler delays.
- Keep GPIO compatibility with distribution libgpiod 1.6 and the 2.x API.
- No service autostart or automatic camera reconnect in this initial stage.

## Alternatives considered

- Generic ROS V4L2 driver: useful candidate for a later controlled test, but
  not validated against ADR-0001/0002. Do not switch capture paths silently.
- Directly port servo angle commands: rejected without an actual position
  sensor, homing procedure, and measured steps-to-angle conversion.
- Reuse bare integer centroids: rejected because dimensions, source time,
  and target absence are needed for independent networked components.
- Neural detector: defer until the simple baseline is measured; no need for
  accelerator/toolchain dependencies in the first learning exercise.

## Evidence

- [Camera buffer decision](ADR-0001-OV5647-THREE-DMA-BUFFERS.md)
- [Camera session/FIFO decision](ADR-0002-OV5647-SINGLE-V4L2-SESSION-AND-FIFO.md)
- [GPIO compatibility](ADR-0004-STEPPER-LIBGPIOD-COMPATIBILITY.md)
- [Implementation and software validation](../worklog/2026-09-09-CHAPTER2-ROS2-FACE-TRACKING.md)

## Consequences

### Positive

Vision can run in the laptop's Jazzy Distrobox while GPIO stays on the Orange Pi.
Camera tuning and ROS development remain separable. Software stop behavior is
testable without hardware, including source loss and both GPIO API shapes.

### Negative

HTTP JPEG transport adds compression/latency and has no sensor exposure stamp.
Haar detection is sensitive to pose/lighting and does not identify a person.
Largest-face selection can switch between people.

### Risks

Reception stamps cannot prove physical image freshness. Estimated steps do not
prove shaft motion or clearance. Software stop cannot guarantee inactive coils
after SIGKILL/OS failure. Releasing coils removes holding torque and may permit
drift. Operator-visible bounded validation remains necessary.

## Validation or review trigger

Revisit after measured image latency, camera mounting, motor direction,
steps/revolution, travel limits, and loaded timing tests. Any direct V4L2
capture change must satisfy or explicitly supersede ADR-0001/0002. Any new
autostart/sustained motion work requires a separate staged experiment.
