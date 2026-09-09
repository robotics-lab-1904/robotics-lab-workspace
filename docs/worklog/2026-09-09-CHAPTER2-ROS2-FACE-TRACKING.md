# Chapter 2: ROS 2 Jazzy face tracking

- Date: 2026-09-09 (started 2026-09-08)
- Status: Completed (software adaptation and validation; hardware integration pending)
- Owner/agent: Codex
- Related task: Adapt ROS Robotics Projects, first edition, Chapter 2.

## Objective

Create reusable ROS 2 packages in `ros-packages` for OV5647 images, face detection, and bounded ULN2003 pan control; explain operation and verify software before powered integration.

## Success criteria

Jazzy build, deterministic safety tests, and a ROS graph integration test using a fixture image and dry-run GPIO. Provide staged single-machine and split-machine instructions. Never imply unperformed hardware validation.

## Environment

### Local workstation

Arch Linux; host Python 3.14.7; no host ROS or OpenCV. Running Ubuntu 24.04.4 Distrobox named `ros-jazzy`, Python 3.12.3 and OpenCV 4.6.0.

### Target hardware

Read-only SSH verifies Orange Pi Zero 3W, AArch64, Ubuntu 24.04 Armbian 26.08.0-trunk, kernel `6.6.98-vendor-sun60iw2`. Existing camera is OV5647. User-confirmed ULN2003 rotation is documented separately; no movement performed here.

### Software versions

SBC: `ros-jazzy-ros-base` 0.11.0-1noble.20260614.091815, `ros-dev-tools` 1.0.1, `python3-libgpiod` 1.6.3-1.1build1, Python 3.12.3. `python3-opencv` is not installed on the SBC.

Container: `ros-jazzy-rclpy` 7.1.11-1noble.20260615.133206,
`ros-jazzy-cv-bridge` 4.1.0-1noble.20260615.144656,
`ros-jazzy-desktop` 0.11.0-1noble.20260616.084553,
`python3-opencv` 4.6.0+dfsg-13.1ubuntu1, NumPy 1.26.4,
`python3-pytest` 7.4.4-1, `python3-colcon-common-extensions` 0.3.0-100,
`ros-jazzy-rosidl-default-generators` 1.6.1-1noble.20260612.064900.

## Initial state

`ros-packages/README.md` contains only a heading. Pre-existing documentation edits, untracked reports, and modified stepper submodule are preserved. Earlier intake described powered motion as pending; updated environment/handoff and the user's powered-motion report now establish user-observed rotation, without characterization measurements.

## Safety and rollback plan

No boot, kernel, service, wiring, camera-submodule, or stepper-submodule edits.
New ROS source lives in the existing `ros-packages` repository; its Git setup
is preserved. Reuse the existing single-client MJPEG server instead of opening
`/dev/video8` from ROS. GPIO defaults to dry-run and disarmed. No live camera
capture or powered tests in unattended validation. Remove the new source
packages and their local build output to roll back software.

## Theory and references

Upstream commit `48d9144293d1b604969ca1208fb813939e935ed9`: grayscale/equalized Haar detection, centroid topic, Dynamixel position increments. Adapt concept to Python/rclpy and explicit timestamped messages. ROS image transport, OpenCV cascades, and the existing vendor camera pipeline are reusable components; generic V4L2 drivers are not yet validated against the lab's three-buffer/single-session requirements.

## Plan

1. Inspect upstream and live environments.
2. Implement interfaces, MJPEG-to-ROS bridge, detector/controller, dry-run-first stepper node.
3. Build and test in Jazzy, including synthetic HTTP and actual ROS messaging.
4. Document bounded hardware verification and remaining calibration.

## Installed or changed packages

No packages installed, removed, or upgraded. Existing container dependencies
were sufficient. Initialized rosdep in the container and downloaded the Jazzy
index. This created `/etc/ros/rosdep/sources.list.d/20-default.list` inside the
container and populated `/home/artm1904/.ros/rosdep/sources.cache` (Distrobox's
shared user home). The latter is dependency metadata, not credentials.

The explicit Ubuntu cascade data prerequisite `opencv-data` is documented
because that name is not a rosdep key; the cascade was already available in the
container at `/usr/share/opencv4/haarcascades/haarcascade_frontalface_default.xml`.

## Created or changed files

Source root: `/home/artm1904/Program/Robot/robotics-lab-workspace/ros-packages`.

| Relative path from source root | Change/purpose | Rollback |
|---|---|---|
| `lab_interfaces/` | New CMake message package: FaceTarget, StepperCommand | Remove new package |
| `lab_camera/` | New Python HTTP MJPEG/fixture bridge, bounded parser and tests | Remove new package |
| `lab_face_tracking/` | New Python detector/controller, YAML/launch and tests | Remove new package |
| `lab_stepper/` | New Python GPIO/dry-run driver, monotonic scheduler and tests | Remove new package |
| `tests/test_ros_graph.py` | Real DDS/rclpy integration over synthetic HTTP | Remove test |
| `README.md`, `THIRD_PARTY_NOTICES.md`, `.gitignore` | Build, staged operation, licensing and artifact separation | Restore README heading/remove new files |
| `.validation/` (ignored) | Local build/install/log, fixture, JUnit and launch log | Remove only generated validation directory |

Documentation: this report, `docs/handoffs/CURRENT.md`,
`docs/agent-context/PROJECT_MAP.md`, `docs/decisions/README.md`, and
`docs/decisions/ADR-0005-ROS2-FACE-TRACKING-BOUNDARIES.md`. Source files are owned
by the development user; no executable bits are required on Python modules
because setuptools installs entry points. No Git commits, pushes, existing
camera/stepper submodule edits, or Gitlink changes were performed.

## Commands executed

Workstation, canonical repository root: `git status --short`, `rg --files`, `cat` relevant context/runbooks/ADRs/template and camera/stepper implementations, `distrobox list`, host Python/OpenCV checks. `git clone --depth 1 https://github.com/PacktPublishing/ROS-Robotics-Projects.git /tmp/ros-book-chapter2-reference` (exit 0); upstream source and license read and commit resolved with `git rev-parse HEAD`.

`distrobox enter ros-jazzy -- bash -lc '…'` inspected `/etc/os-release`, Python, ROS packages and OpenCV. Read-only `ssh -o BatchMode=yes -o ConnectTimeout=5 root@192.168.1.236 '…'` inspected OS, kernel and dpkg versions. No secrets printed or stored.

Dependency setup/check inside `ros-jazzy`:

```bash
sudo -n rosdep init
rosdep update --rosdistro jazzy
source /opt/ros/jazzy/setup.bash
cd /home/artm1904/Program/Robot/robotics-lab-workspace/ros-packages
rosdep check --from-paths lab_camera lab_interfaces lab_stepper lab_face_tracking \
  --ignore-src --rosdistro jazzy
```

Initial check found manifest errors; after correction, it printed
`All system dependencies have been satisfied` (exit 0).

Build inside `ros-jazzy`, from the source root, with only Jazzy sourced:

```bash
mkdir -p .validation
touch .validation/COLCON_IGNORE
colcon --log-base .validation/log build \
  --base-paths lab_interfaces lab_camera lab_stepper lab_face_tracking \
  --build-base .validation/build --install-base .validation/install \
  --symlink-install --executor sequential
```

First build: four packages finished in 10.1 seconds (exit 0). Rebuild after
manifest corrections: four packages finished in 3.87 seconds (exit 0).

Fixture fetched on the workstation from OpenCV's `4.6.0` tag into
`ros-packages/.validation/fixtures/lena.jpg` with `curl -fL --max-time 30` (exit 0).
Size: 91,814 bytes. SHA-256:
`7de7ed51a1594fff247f4cae2301eceacf5313d6011e37b4a4c8733f7bb72c07`.

Tests inside the container, from the source root:

```bash
source /opt/ros/jazzy/setup.bash
source .validation/install/local_setup.bash
export ROS_DOMAIN_ID=83
export ROS_AUTOMATIC_DISCOVERY_RANGE=LOCALHOST
export ROS_LOG_DIR=/tmp/chapter2-ros-logs
export CHAPTER2_FACE_FIXTURE="$PWD/.validation/fixtures/lena.jpg"
python3 -m pytest lab_camera/test lab_face_tracking/test lab_stepper/test tests \
  -q --junitxml=.validation/pytest.xml
```

Launch smoke test in a separate container shell, same source root and overlay:

```bash
export ROS_DOMAIN_ID=84
export ROS_AUTOMATIC_DISCOVERY_RANGE=LOCALHOST
export ROS_LOG_DIR=/tmp/chapter2-launch-logs
timeout 25s ros2 launch lab_face_tracking chapter2.launch.py \
  image_path:="$PWD/.validation/fixtures/lena.jpg" with_stepper:=true max_frames:=20
```

Output saved to `.validation/launch-smoke.log`; exit 0. Four processes started;
the camera published exactly 20 frames, then all processes exited cleanly.
Driver log explicitly recorded `dry_run=True; DISARMED`.

## Experiments

### EXP-ROS2-001: Deterministic parser and motion validation

- Hypothesis: partial HTTP reads, stale commands and travel limits can be
  handled independently of the hardware drivers.
- Changed variable: synthetic bytes, clocks, face boxes, rates, and fake GPIO APIs.
- Procedure: pytest package tests, including v1/v2 request/release mocks.
- Measurements: 37 unit cases passed.
- Result: fragmented multipart frames accepted; oversized/malformed frames
  rejected; deadband, saturation, age checks, reversal, timeout, session limits,
  disarm, no catch-up, GPIO cleanup and optional import behavior verified.
- Interpretation: control policy and backend API shape work under these tests;
  actual device timing is not measured.
- Next experiment: observer-supervised bounded physical steps.

### EXP-ROS2-002: Complete ROS graph with a synthetic HTTP camera

- Hypothesis: a real face image can drive a simulated pan motor through the
  same published interfaces intended for split-machine operation.
- Changed variable: local HTTP source alternates a face image, blank image,
  restored face, and stalled stream. Separate case injects old timestamps.
- Procedure: real rclpy nodes and DDS, actual OpenCV detection, SetBool service,
  annotated image subscriber, and dry-run driver.
- Measurements: 2 integration cases passed. Detected target was in the right
  half of a 1024×512 composite; annotation dimensions matched; rate stayed <=40
  half-steps/s; no motion before enable; step count increased after enable.
- Result: blank frames and stalled transport stopped steps and released
  simulated coils; a five-second-old target generated zero motion. Exactly one
  HTTP connection, without automatic reconnect.
- Interpretation: software data flow and failure handling pass on x86_64 Jazzy.
- Next experiment: replace synthetic HTTP with a 100-frame OV5647 run, motors
  omitted; then validate remote dry-run commands before powered integration.

### EXP-ROS2-003: Actual launch process lifecycle

- Hypothesis: installed entry points/config/launch can start and stop together.
- Procedure: bounded 20-frame fixture launch with simulated, disarmed stepper.
- Result: four processes started, published 20 frames, then clean shutdown;
  timeout wrapper did not fire (exit 0).

## Errors and diagnosis

Sandboxed container inspection failed accessing `/run/user/1000/libpod`; sandboxed SSH failed on system SSH config ownership. Explicit escalation resolved both. SBC dpkg check exited 1 because OpenCV is absent; this is a dependency observation, not a ROS failure.

- First pytest run: 38 passed, one failed. The test checked the camera's
  `finished` flag immediately when the worker thread set `error`, before the
  ROS timer had observed it. Corrected the test to wait for the externally
  visible finished state; no production behavior was changed for this race.
- Initial rosdep calls failed because its index was uninitialized. After
  initialization, check exited 2 for nonexistent `ament_python` and `opencv-data`
  rosdep keys. Replaced the build dependency with `python3-setuptools`, keeping
  `ament_python` only as build type, and documented cascade data as an explicit
  Ubuntu prerequisite. Recheck passed.
- rosdep emitted a `pkg_resources` deprecation warning from its installed
  entrypoint. Index update and final check succeeded; it was not a task failure.
- Final ownership check corrected an initial assumption that `ros-packages`
  belonged directly to the superproject. `git -C ros-packages rev-parse
  --show-toplevel` identifies an independent repository at that directory,
  with HEAD `44d0c59` (`first commit`); `.git` points to
  `../.git/modules/ros-packages`. The parent `.gitmodules` already configures
  its remote, but `git ls-files --stage -- ros-packages` has no entry and
  `git submodule status -- ros-packages` exits 1. Registration is incomplete
  in the parent index; the task did not change/stage/commit Git metadata.
  Ownership notes were corrected; future source commits must happen inside
  `ros-packages`, then the parent can record its gitlink. No source was added
  as ordinary parent-repository files.

## Rejected hypotheses

Do not assume ros-base supplies OpenCV or that a generic camera node can safely open this vendor V4L2 stack. Do not translate half-steps into radians without measured calibration.

## Validation

Final result: **39 tests passed in 2.68 seconds**, exit 0. JUnit artifact:
`ros-packages/.validation/pytest.xml`. Four-package rebuild and rosdep check
passed. Launch smoke passed with clean exit. `git diff --check` passed.

No live camera capture, GPIO request, motor movement, AArch64 build, networked
DDS test, GUI session, NPU work, or sustained-load test was run. These require
the next staged experiment; the current software task deliberately uses an
isolated local synthetic stream and simulated GPIO.

## Final result

Four buildable ROS 2 packages and a staged guide are implemented. The first
version reuses the existing camera path and distribution OpenCV; supports
laptop vision/Orange Pi motion, explicit arm/disarm, target loss handling,
clock checks, bounded estimated travel, and per-process motion budgets.
No hardware software was replaced or deployed and no system service changed.

## Limitations and open questions

Exact motor model/gear ratio, direction under the camera mount, physical travel limits, camera latency, clock synchronization, and sustained tracking remain unverified.

Image stamps are reception timestamps; they cannot detect all upstream camera
buffering. Haar detection can miss faces or switch between people. Estimated
step counts cannot detect missed steps or drift after coils release. Initial
phase alignment is not measured. Physical limit switches/homing are absent;
software limits are not a physical safety guarantee. Laptop GUI/Distrobox
network access has not been validated by these localhost tests.

## Reproduction from a clean state

Follow [the package guide](../../ros-packages/README.md): install development
tools and `opencv-data` in the vision environment, initialize rosdep if needed,
link the source collection into a separate workspace, resolve dependencies,
build and source. Run a JPEG fixture launch and the documented tests first.
For the GPIO host, build only through `lab_stepper` and explicitly install
distribution `python3-libgpiod`. All optional fixtures/builds stay out of Git.

## Rollback

Stop new ROS processes; remove only new source/build artifacts if unwanted. Existing hardware software remains untouched.

The new rosdep configuration can be removed from the container if unwanted;
do not delete the shared user cache if another workspace is using it. No package
downgrade, board recovery, or boot rollback is required.

## Next steps

1. Run the 100-frame OV5647 vision launch, motor omitted, following the camera
   runbook and ensuring no browser stream client owns the camera.
2. Verify synchronized clocks and laptop-to-board DDS discovery with dry-run.
3. Reverify GPIO ownership/wiring, then perform observer-supervised motion with
   ±8 estimated half-step limits and an eight-step total budget.
4. Measure direction, mounting clearance, gearbox ratio, latency and load before
   increasing limits or attempting sustained closed-loop tracking.

## Learning topics

ROS 2 packages and interfaces; QoS and timestamps; image coordinates and deadband; velocity commands versus measured position; monotonic watchdogs; GPIO ownership.

## Sources

- [Book code](https://github.com/PacktPublishing/ROS-Robotics-Projects/tree/48d9144293d1b604969ca1208fb813939e935ed9/Chapter02)
- [OpenCV Haar detection](https://docs.opencv.org/4.x/d2/d99/tutorial_js_face_detection.html)
- [ROS 2 V4L2 camera candidate](https://github.com/tier4/ros2_v4l2_camera)
- [Camera runbook](../runbooks/OV5647_CAMERA.md)
- [Stepper runbook](../runbooks/ULN2003_STEPPER_MOTOR.md)
- [Powered-motion report](2026-09-08-STEPPER-POWERED-MOTION-VALIDATION.md)
- [Implementation decision](../decisions/ADR-0005-ROS2-FACE-TRACKING-BOUNDARIES.md)
- [OpenCV 4.6.0 fixture](https://github.com/opencv/opencv/blob/4.6.0/samples/data/lena.jpg)
