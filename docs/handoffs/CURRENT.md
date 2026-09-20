# Current Handoff

Last updated: 2026-09-20

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

- The four executable nodes now have C++17 implementations. The normal
  executable names select C++; the preserved Python implementations live under
  each package's `python/` directory and use `_py` executable suffixes. The
  launch argument `implementation:=cpp|python` defaults to C++. See the
  [C++ walkthrough](../../ros-packages/CPP_WALKTHROUGH.md) and
  [port report](../worklog/2026-09-20-ROS2-CPP-NODE-PORT.md).
- The three implementation packages now use `ament_cmake` plus
  `ament_cmake_python`. The C++ code separates MJPEG parsing, tracking/control
  math, and bounded motor scheduling from thin ROS adapters. The stepper backend
  conditionally supports libgpiod 1.x and 2.x APIs at compile time.
- Jazzy Distrobox validation passed: all four packages built, 53 C++/Python
  tests passed, both language launch choices completed bounded fixture runs,
  a C++ target was decoded over DDS, and the C++ dry-run stepper reached an
  exact three-step session limit with coils inactive. `libgpiod-dev`
  `1.6.3-1.1build1` was installed in that Distrobox for compilation.
- The C++ refactor has not been deployed or built on the Orange Pi. Next install
  `libgpiod-dev` there, rebuild on AArch64, run a bounded local-JPEG graph, then
  replay real OV5647 tracking in dry-run before any observed powered test. The
  source refactor itself did not access camera or GPIO hardware.

- User selected Chapter 2 face tracking from Lentin Joseph's *ROS Robotics
  Projects*, first edition (2017). Four packages now exist under `ros-packages`:
  `lab_interfaces`, `lab_camera`, `lab_face_tracking`, `lab_stepper`.
- A beginner-oriented [code walkthrough](../../ros-packages/CODE_WALKTHROUGH.md)
  now explains ROS package/build concepts, every source layer and library, the
  complete asynchronous camera-to-motor flow, a numerical control example,
  live introspection commands, and a recommended reading order.
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
- First Orange Pi launch on 2026-09-10 exposed one missing runtime prerequisite:
  `opencv-data` is not installed, so the detector cannot load
  `/usr/share/opencv4/haarcascades/haarcascade_frontalface_default.xml`.
  Noble arm64 offers version `4.6.0+dfsg-13.1ubuntu1` from enabled `universe`.
  Install and verify that package, then repeat the dry-run launch; no colcon
  rebuild is required. The failed launch correctly stopped all other nodes.
- After installing the cascade data, the real OV5647-to-laptop GUI path passed:
  `/face/image` appeared in `rqt_image_view` over DDS and showed the red centre
  line. A repeated 300-frame dry-run launch exited 0; all four processes stopped
  cleanly, with 667 incoming frames superseded before publication. The stepper
  remained simulated and disarmed. Next validate a frontal face on
  `/face/target`, then explicitly arm dry-run before planning real GPIO.
- Laptop `ros2 topic echo /face/target` currently cannot decode the custom type:
  its `/home/artm1904/ros2_ws` has the correct source symlink but no `install/`
  directory. Build `lab_interfaces` in the laptop Distrobox, source
  `~/ros2_ws/install/setup.bash`, and echo with best-effort QoS. The standard
  `/face/image` works without this overlay because `sensor_msgs/Image` ships
  with Jazzy.
- Resolved 2026-09-16: the laptop built and sourced `lab_interfaces`; its prefix
  and interface definition are visible, and a live best-effort echo decoded a
  1280×720 `FaceTarget` message successfully. Continue with frontal-face
  detection and explicitly armed dry-run motion.
- Laptop GUI latency was traced to raw `/face/image`: each 1280×720 BGR8 message
  is 2,700 KiB, and a live probe received only 6 in 10 seconds. Use
  `/face/image/compressed` in `rqt_image_view`; measured JPEGs were about 70 KiB
  with roughly 0.35–0.49 s header delay. Orange Pi CPU was also high during the
  snapshot, so optimize compute/timers before powered closed-loop tracking.
- Selecting `/face/image/compressed` currently fails on the laptop because its
  Distrobox declares only `image_transport/raw_sub`. Install
  `ros-jazzy-compressed-image-transport` in that same container, restart RQt
  after sourcing Jazzy and the workspace, and verify the compressed subscriber
  plus perceived latency. This is a missing laptop plugin, not a DDS or Orange
  Pi publisher failure.
- The user installed that plugin successfully (`ros2 pkg prefix` resolves to
  `/opt/ros/jazzy`). Do not launch RQt with `/face/image/compressed` as a
  positional argument: Jazzy interprets that literal as a raw topic and hits an
  incompatible-type error. Launch with no topic argument, refresh, and select
  `/face/image/compressed` from the dropdown; final display/latency validation
  remains pending.
- RQt saved the bad literal and subsequently restored it even on a no-argument
  launch, causing the same immediate crash. Recover once with
  `ros2 run rqt_image_view rqt_image_view /face/image`, select the compressed
  entry in the open GUI, and exit normally. Use `rqt --clear-config` only as a
  broader fallback because it resets other RQt preferences too.
- ROS stepper preflight passed on 2026-09-16. An eight-step dry-run reached the
  exact session limit and automatically disarmed with coils inactive. A real
  GPIO zero-motion run then enabled at 0 steps, sent no command, explicitly
  disarmed, and released all four consumers. After release, `gpioinfo` showed
  the lines unused but still configured as outputs. Direct SIGINT printed an
  `rclpy` invalid-context traceback despite successful final cleanup. The next
  step is an operator-observed, maximum-eight-half-step powered command with an
  immediate physical power disconnect available.
- The subsequent powered attempt did not execute: SSH timed out before the
  remote script started, and the board then failed three ping probes despite a
  correct local Wi-Fi route. No powered GPIO command from that attempt reached
  the board. Motor 5 V must remain disconnected until board power/network state
  is physically checked and SSH plus idle GPIO state are reverified.
- Resolved 2026-09-19: the user restored reachability and the board had rebooted.
  SSH, idle process state, and initially unclaimed GPIO inputs passed. A repeated
  post-reboot real-GPIO zero-motion enable/disarm also passed and released all
  consumers. The prior outage cause remains unverified. Before the eight-step
  movement, confirm that motor 5 V—previously disconnected on instruction—is
  switched on with the motor visible and its disconnect immediately available.
- The powered eight-half-step ROS test then completed on 2026-09-19: one fresh
  +40 half-step/s command reached exactly 8 session steps, automatically
  disarmed for `session_limit`, reported coils inactive, and released all GPIO
  consumers. SSH remained reachable and the immediate filtered kernel log was
  quiet. The operator confirmed smooth correct movement of the motor and
  attached camera to the right. Positive command therefore means camera-right
  for the current wiring and mount, supporting the existing `direction: 1`
  polarity for an unmirrored image. Full automatic face tracking, sustained
  operation, and physical position feedback remain unvalidated.
- The next documented procedure is a full but bounded automatic loop: run the
  300-frame camera/detector/controller launch with `with_stepper:=false`, run a
  separate stepper with ±16 travel and a 16-step session budget, rehearse with
  `dry_run:=true`, then repeat once with real GPIO under direct observation.
  Explicitly disarm afterward; do not use continuous powered tracking yet.
- First automatic powered attempt diagnosed: the ROS graph was connected and
  the real stepper consumed all 16 steps, netting +12 before automatic
  `session_limit` disarm. Current target/command were false/zero; all targets in
  an eight-second sample were false, and a captured annotated frame showed only
  an empty sofa. Restore a visible red face rectangle and verify
  `detected=true` before starting any fresh bounded motor process.
- A brief face appearance produced one true target at x=-0.7875 and the fresh
  stepper immediately consumed its 16-step budget toward the negative limit.
  The next six seconds contained 27 targets, 74 commands, zero detections, and
  zero nonzero rates; another frame again showed the empty sofa. Keep the user
  physically in the field of view until RQt shows a stable red rectangle before
  any further powered trial.
- Stable tracking was then achieved: 57/57 targets detected the face at x about
  -0.42 to -0.47, producing 121/121 negative commands. A fresh dry-run completed
  the automatic loop to exactly -16 and session-limit disarm. The old real node
  was stopped and GPIO is unclaimed. Do not start another real session until
  the operator confirms the mount can safely move farther left; restarting
  resets estimated zero without homing.
- Operator confirmed 30–40 degrees of clearance. A gated real run required ten
  consecutive off-centre detections, passed at average x=-0.652, and explicitly
  armed a ±16/16-step real node. Its final status echo timed out, triggering
  fail-closed cleanup. Postflight showed no motor process/node, no GPIO
  consumers, no matching immediate kernel errors, and reachable SSH. Await the
  operator's report of physical movement; do not infer exact steps because the
  final status was not captured.
- Do not remove all motion limits. A follow-up isolated the stepper on
  `/pan/manual_command` and recorded 60 positive real-GPIO transitions at
  40 half-steps/s with ±64/64-step bounds before watchdog stop and clean GPIO
  release. Await physical observation: movement means the earlier 16-step limit
  and unstable detection obscured behavior; no movement points to power,
  ground, ULN2003, wiring, or mechanical state downstream of ROS scheduling.
- A user-requested larger isolated run completed exactly 200 positive real-GPIO
  transitions at 40 half-steps/s, hit `session_limit`, de-energized, and
  released all consumers. The operator confirmed visible rightward camera
  movement. The complete motor path works; 16 and 60 steps were simply not
  visually apparent. Use one directly observed ±200/200-step session for the
  next automatic trial, never unrestricted motion, because process restart
  resets estimated zero without homing.
- User later ran the real driver at max rate 120, ±600, and session budget
  2,000,000. Live inspection showed automatic tracking still capped by
  pan-controller max rate 40/gain 80. The enabled idle node had accumulated 407
  steps and was safely disarmed/released. To increase tracking speed, tune both
  controller max rate and gain in stages (60/100, 80/120, then an observed
  120/160 test) while keeping the driver ceiling at least as high. Restore a
  bounded 600–1200 session; do not use millions of reversible transitions
  without homing, limit switches, feedback, and thermal/travel measurements.
- A linear post-reboot guide now exists at
  `docs/runbooks/ROS2_FACE_TRACKING_ORANGE_PI.md`, including commands, option
  tables, monitoring, cleanup, and laptop viewing. Canonical Chapter 2 defaults
  now match the validated gain/rates/travel (160, 120, ±600) with a safer 1200
  session budget. The live node was found armed and idle at 2,187 transitions;
  it was explicitly disarmed and released. The runbook has not yet been replayed
  end-to-end after an actual reboot.
- User confirmed no movement in the 60-step isolated run. A subsequent 2 Hz,
  eight-step test captured debugfs GPIO levels walking correctly across all four
  expected offsets, reached the exact session limit, and released consumers.
  The fault is now downstream of logical GPIO: power down, then check ULN2003
  supply/power LED, shared ground, IN1–IN4 signal wiring/LED sequence, motor
  connector, driver outputs, and mechanical binding. Do not remove limits.
- Read-only follow-up on 2026-09-09 found a clean board clone at `817b8f8` under
  `/root/ros2_ws/src/ros-packages`; all four packages are discoverable and an
  older overlay exists. Required OpenCV/cv_bridge/libgpiod packages and device
  nodes are present, NTP is synchronized, and no camera capture process was
  active. Rebuild before running. Both board and laptop Distrobox use subnet
  discovery; verify DDS across Wi-Fi because the laptop also has a VPN interface.
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
