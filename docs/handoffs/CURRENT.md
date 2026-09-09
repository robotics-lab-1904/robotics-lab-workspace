# Current Handoff

Last updated: 2026-09-09

## Current state

- `robotics-lab-workspace` is the active superproject at
  `/home/artm1904/Program/Robot/robotics-lab-workspace`.
- Four submodules are registered and pinned: camera, stepper motor, upstream
  Armbian build, and the Orange Pi kernel fork.
- The kernel submodule points to `robotics/ov5647-sun60iw2` at `4590a2f`.
- The Armbian customization is stored as
  `patches/armbian/0001-enable-ov5647-sun60iw2.patch`; the submodule remains an
  upstream checkout and becomes dirty only when this patch is applied.
- Internal Markdown navigation uses local relative links across superproject
  and submodule boundaries; the recursive superproject checkout is canonical.
- One OV5647 camera is operational on `/dev/video8`.
- A 10000-frame V4L2 test succeeded at approximately 31.27 FPS with three DMA buffers.
- FFmpeg MJPEG transfer works through a named FIFO.
- Browser streaming works on port 8081.
- The web UI includes an English debug panel backed by `/status.json`.
- Persistent journald storage is enabled.
- The systemd camera service is installed but should remain disabled until reboot behavior is validated.

## Next recommended work

1. Rotate the board SSH password because the previous credential existed in
   commit `5f5ac26`; deleting it from the current files does not remove it from
   Git history.
2. Commit and push documentation corrections in each changed submodule, then
   update and commit the corresponding superproject gitlink.
3. Validate the complete workspace through a clean `--recurse-submodules`
   clone and verify the Armbian patch with
   `bash patches/armbian/apply_patch.sh --check`.
4. Restart the updated camera server and verify the debug panel after a hard browser refresh.
5. Measure actual FPS, bitrate, CPU load, temperature, and latency at 20, 25, and 30 output FPS.

## Stepper motor status

- An interactive ULN2003 controller supporting the board's libgpiod 1.6.3 and
  newer 2.x APIs is deployed under `/root/stepper-motor/`; all three local tests,
  traced dry-run, and live zero-motion GPIO request/release pass.
- Live pinctrl verified gpiochip0 offsets PE13=141, PD3=99, PB6=38, PD4=100 as
  unclaimed. The user subsequently assembled the stated header-to-ULN2003
  wiring and reported correct powered motor rotation on 2026-09-08.
- Exact test parameters and measurements were not captured. Next motor work is
  Stage 5 characterization: steps per output revolution, current, temperature,
  load, reliable speed range, missed steps, and sustained operation. Stop on
  heat, unstable power, resets, or unexpected behavior.

## ROS 2 Chapter 2 implementation

- User selected Chapter 2 face tracking from Lentin Joseph's *ROS Robotics
  Projects*, first edition (2017). Four packages now exist under `ros-packages`:
  `lab_interfaces`, `lab_camera`, `lab_face_tracking`, `lab_stepper`.
- Board Ubuntu 24.04/Jazzy verified through read-only SSH. Laptop Arch host has
  a working Ubuntu 24.04.4 `ros-jazzy` Distrobox with Python 3.12.3/OpenCV 4.6.0.
  No packages installed; rosdep initialized and its Jazzy index downloaded there.
- Four packages build in Distrobox; 39 unit/integration tests pass, including
  synthetic HTTP camera, real OpenCV/DDS, service arming and dry-run motion.
  A 20-frame installed launch test exits cleanly. Generated files are ignored in
  `ros-packages/.validation`; no source was deployed to the board.
- `ros-packages` is an existing independent repository (HEAD `44d0c59`) with
  a `.gitmodules` entry but no parent index gitlink yet. Source changes remain
  uncommitted. Commit there first, then record its gitlink in the parent; do not
  stage its source as ordinary superproject files. Git metadata was not changed.
- Next: 100-frame real OV5647 vision test (no motor), split-machine DDS/clock
  verification in dry-run, then observer-supervised eight-half-step integration.
- Keep the existing MJPEG server as camera owner. Close browser image clients
  before the ROS bridge connects. Motor defaults to simulated and disarmed;
  explicit enable, source-age checks, watchdog and travel/session budgets apply.
- [Build and staged operation guide](../../ros-packages/README.md)
- [Implementation report](../worklog/2026-09-09-CHAPTER2-ROS2-FACE-TRACKING.md)
- [ADR-0005](../decisions/ADR-0005-ROS2-FACE-TRACKING-BOUNDARIES.md)

## Camera operating constraints

- Keep `--stream-mmap=3`.
- Keep selection, format, and streaming in one `v4l2-ctl` process.
- Use FIFO/file isolation between V4L2 raw output and FFmpeg.
- Do not permit concurrent camera clients.

## Key references

- `docs/worklog/2026-08-23-OV5647-CAMERA-BRINGUP.md`
- `docs/runbooks/OV5647_CAMERA.md`
- `docs/decisions/ADR-0001-OV5647-THREE-DMA-BUFFERS.md`
- `docs/decisions/ADR-0002-OV5647-SINGLE-V4L2-SESSION-AND-FIFO.md`
- `docs/worklog/2026-08-29-ULN2003-STEPPER-CLI.md`
- [Stepper compatibility](../agent-context/STEPPER_MOTOR_COMPATIBILITY.md)
- [Stepper runbook](../runbooks/ULN2003_STEPPER_MOTOR.md)
- [ADR-0004: stepper libgpiod compatibility](../decisions/ADR-0004-STEPPER-LIBGPIOD-COMPATIBILITY.md)
- [Documentation worklog](../worklog/2026-09-08-STEPPER-DOCUMENTATION-AND-COMPATIBILITY.md)
- [Powered-motion validation](../worklog/2026-09-08-STEPPER-POWERED-MOTION-VALIDATION.md)
