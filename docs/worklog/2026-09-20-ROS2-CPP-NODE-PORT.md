# ROS 2 Chapter 2 C++ Node Port

- Date: 2026-09-20
- Status: Completed locally; Orange Pi deployment pending
- Owner/agent: Codex
- Related issue/task: Preserve the Python implementation and add a simpler, extensible C++ implementation of every Chapter 2 node.

## Objective

Port `mjpeg_camera`, `face_detector`, `pan_controller`, and `stepper_node` to
C++ while preserving the existing Python implementation in explicit
`python/` directories.

## Success criteria

- Every implementation package has `python/` and `cpp/` source directories.
- C++ nodes preserve the existing ROS topics, services, parameters, QoS, and
  motor safety behavior.
- Existing Python nodes remain buildable and runnable with distinct executable
  names.
- The launch file can select C++ or Python and defaults to C++.
- The complete workspace builds and meaningful unit/integration checks pass.

## Environment

### Local workstation

- Canonical checkout: `/home/artm1904/Program/Robot/robotics-lab-workspace`
- Host: Arch Linux; ROS validation is intended for the Ubuntu 24.04 Jazzy
  Distrobox when available.

### Target hardware

- Orange Pi Zero 3W, Ubuntu 24.04 base, ROS 2 Jazzy.
- OV5647 stream through the existing local MJPEG server.
- ULN2003 on `/dev/gpiochip0`, offsets `[141, 99, 38, 100]`.

### Software versions

- ROS 2 Jazzy in Ubuntu 24.04 Distrobox
- GCC 13.3.0
- OpenCV 4.6.0
- cv_bridge 4.1.0
- libgpiod development API 1.6.3

## Initial state

The three implementation packages use `ament_python`. The four nodes and their
pure logic helpers are implemented only in Python. The working ROS graph and
bounded motor behavior are documented in ADR-0005 and the Orange Pi runbook.
The repositories already contain unrelated uncommitted documentation and
configuration changes; they will be preserved.

## Safety and rollback plan

This task changes source and build metadata only. No remote command, GPIO
request, camera access, or powered motor operation is part of validation.
Rollback is a source-level revert of the files listed below.

## Theory and references

- `docs/decisions/ADR-0005-ROS2-FACE-TRACKING-BOUNDARIES.md`
- `docs/runbooks/ROS2_FACE_TRACKING_ORANGE_PI.md`
- Existing Python implementation under `ros-packages/`.

## Plan

1. Preserve Python sources under per-package `python/` directories.
2. Convert implementation packages to `ament_cmake` plus
   `ament_cmake_python`.
3. Add small C++ core classes/functions separated from ROS node adapters.
4. Add C++ executables and Python wrapper executables.
5. Add launch implementation selection and update operating documentation.
6. Build and test without touching hardware.

## Installed or changed packages

The workstation host was not changed. The following packages were installed in
the existing `ros-jazzy` Distrobox:

| Package | Version | Source | Reason | Direct/dependency |
|---|---|---|---|---|
| `libgpiod-dev` | `1.6.3-1.1build1` | Ubuntu Noble universe | Compile the C++ GPIO backend | Direct |
| `libgpiod2t64` | `1.6.3-1.1build1` | Ubuntu Noble universe | Runtime library selected by apt | Dependency |

## Created or changed files

| Path | Change | Purpose | Owner/mode | Rollback |
|---|---|---|---|---|
| `ros-packages/lab_camera/python/` | Moved preserved Python modules; added `_py` wrapper | Keep the original implementation runnable | Existing source; wrapper executable | Restore old directory and build metadata |
| `ros-packages/lab_camera/cpp/` | Added bounded multipart parser and C++ camera node | Default C++ MJPEG bridge | Source | Remove C++ tree and restore Python executable name |
| `ros-packages/lab_face_tracking/python/` | Moved preserved Python modules; added two `_py` wrappers | Keep detector/controller reference implementation | Existing source; wrappers executable | Restore old directory and build metadata |
| `ros-packages/lab_face_tracking/cpp/` | Added tracking helpers, face detector, controller, and tests | Default C++ vision/control path | Source | Remove C++ tree and restore Python executable names |
| `ros-packages/lab_stepper/python/` | Moved preserved Python modules; added `_py` wrapper | Keep original motor implementation runnable | Existing source; wrapper executable | Restore old directory and build metadata |
| `ros-packages/lab_stepper/cpp/` | Added motion core, libgpiod backends, safe node adapter, and tests | Default C++ motor path | Source | Remove C++ tree and restore Python executable name |
| Three package `CMakeLists.txt` and `package.xml` files | Converted implementation packages to `ament_cmake` plus `ament_cmake_python` | Build both languages in one package | Source | Restore `ament_python` manifests |
| `ros-packages/lab_face_tracking/launch/chapter2.launch.py` | Added `implementation:=cpp|python`, default C++ | Select a complete implementation consistently | Source | Remove selector and use explicit executables |
| `ros-packages/README.md`, `CPP_WALKTHROUGH.md`, `CODE_WALKTHROUGH.md` | Documented source layout, commands, and extension points | Reproducible development | Source | Revert documentation |
| `docs/runbooks/ROS2_FACE_TRACKING_ORANGE_PI.md` | Added C++ dependency and implementation commands | Prepare later board deployment | Source | Revert documentation |

## Commands executed

Workstation, repository inspection only:

```bash
git status --short --branch
git -C ros-packages status --short --branch
rg / sed / find over relevant context, ADR, runbook, package, launch, source,
and test files
```

Purpose: establish repository boundaries and preserve all existing behavior.

Result: three `ament_python` implementation packages and four node executables
identified. No nested `AGENTS.md` applies under `ros-packages`.

Distrobox dependency and build:

```bash
sudo apt-get install -y libgpiod-dev
source /opt/ros/jazzy/setup.bash
colcon build --symlink-install --executor sequential
```

Result: all four packages built. The installed executable inventory contains
the four normal C++ names and four `_py` Python names.

Distrobox tests:

```bash
colcon test --packages-select lab_camera lab_interfaces lab_stepper lab_face_tracking
colcon test-result --verbose
```

Result: 53 tests, 0 errors, 0 failures, 0 skipped.

Bounded installed-graph checks:

```bash
ros2 launch lab_face_tracking chapter2.launch.py \
  implementation:=cpp image_path:=<LENA_JPEG> max_frames:=5 \
  with_stepper:=true dry_run:=true

ros2 launch lab_face_tracking chapter2.launch.py \
  implementation:=python image_path:=<LENA_JPEG> max_frames:=5 \
  with_stepper:=true dry_run:=true
```

Result: both graphs started all four selected executables and shut down cleanly
when the bounded camera completed. All stepper nodes remained dry-run and
disarmed.

## Experiments

### EXP-CPP-001: C++ face target through DDS

- Hypothesis: the installed C++ camera and detector preserve the custom message
  contract.
- Changed variable: selected `implementation:=cpp` with a local JPEG fixture.
- Procedure: launched 30 frames and echoed one best-effort `/face/target`.
- Measurements: `detected=true`, normalized centre `(0.18359375, 0.12890625)`,
  image size `512x512`, preserved camera frame ID and timestamp.
- Result: passed; the launch exited cleanly after 30 frames.
- Interpretation: JPEG decode, Haar detection, custom C++ typesupport, DDS, and
  launch shutdown work together.

### EXP-CPP-002: C++ dry-run stepper session limit

- Hypothesis: the installed C++ node arms explicitly, accepts fresh stamped
  commands, and releases at its finite session budget.
- Changed variable: dry-run with `max_session_steps:=3`.
- Procedure: enabled through `/pan/enable`, published fresh 100 half-step/s
  commands, then read `/pan/status`.
- Measurements: estimated position `3`, session steps `3`, enabled `false`,
  coils active `false`, reason `session_limit`.
- Result: motion/safety behavior passed without GPIO access.
- Interpretation: the C++ ROS adapter preserves the tested pure scheduler
  behavior.

## Errors and diagnosis

- The first colcon invocation placed `--log-base` after `build`; this colcon
  version requires the global option before the verb. The corrected invocation
  built normally.
- `lab_stepper/package.xml` initially declared three dependencies as both
  generic and execution dependencies. `catkin_pkg` rejected the redundancy;
  the duplicate execution tags were removed.
- libgpiod 1.6 declares the offsets argument of `gpiod_chip_get_lines` as
  mutable. The C++ backend now passes a local mutable copy and compiles against
  the board-compatible 1.6 API.
- The shell harness sent SIGINT to `ros2 run`, which did not forward it to the
  background C++ child. The child and wrapper were found and terminated. This
  did not affect the observed session-limit result. Launch-managed C++ shutdown
  exited cleanly in both bounded graph tests.

## Rejected hypotheses

- Reusing the old `ament_python` build type for mixed C++/Python packages was
  rejected because it cannot build native targets. `ament_cmake_python` keeps
  the Python modules in the same package without deleting them.
- Keeping identical executable names for both languages was rejected because
  `ros2 run` must resolve one installed file deterministically. C++ keeps the
  existing names; Python uses explicit `_py` names.

## Validation

- Plain C++ compilation of the three pure helpers passed on the host.
- All packages built in the Jazzy Distrobox with no compiler warnings in the
  task output.
- 53 C++ and preserved Python tests passed.
- C++ and Python bounded installed launch graphs exited 0.
- C++ DDS target output and dry-run three-step session limit passed.
- `rosdep resolve libgpiod-dev` returned Ubuntu package `libgpiod-dev`, and
  `rosdep check` reported all dependencies satisfied.
- SHA-256 comparison against `ros-packages` HEAD confirmed that all eleven
  moved Python module files are byte-for-byte unchanged.
- `git diff --check` passed in both the superproject and `ros-packages`.
- No camera device or GPIO hardware was accessed.

## Final result

The four nodes now have C++17 defaults and preserved Python alternatives. Pure
logic is separated from ROS adapters, and the launch file selects one complete
language implementation. Existing topic names, custom messages, QoS, service,
parameters, stale-data checks, and bounded motor behavior are retained.

## Limitations and open questions

- The C++ camera client intentionally supports unencrypted `http://`, which is
  the lab's loopback/LAN MJPEG transport. The preserved Python client also
  accepts HTTPS.
- libgpiod 1.6 compiled and dry-run behavior was tested. The conditional 2.x
  source path was not compiled in this Noble environment.
- The code was not yet built on AArch64 or deployed to the Orange Pi.
- Real OV5647 streaming, real GPIO requests, and powered movement were not run
  during this source refactor. They require the existing staged runbook.

## Reproduction from a clean state

```bash
sudo apt install ros-dev-tools opencv-data libgpiod-dev python3-libgpiod
source /opt/ros/jazzy/setup.bash
cd ~/ros2_ws
rosdep install --from-paths src/ros-packages --ignore-src --rosdistro jazzy -y
colcon build --symlink-install --executor sequential
source install/setup.bash
ros2 launch lab_face_tracking chapter2.launch.py implementation:=cpp
```

## Rollback

Revert the task-specific source, build metadata, launch, documentation, and
test changes. The only non-source rollback is removing `libgpiod-dev` and its
now-unused apt dependency from the Distrobox if desired. No hardware state was
changed by this task.

## Next steps

1. Pull/copy the source to the Orange Pi and install `libgpiod-dev`.
2. Build all four packages on AArch64.
3. Replay a bounded JPEG-fixture launch, then the real OV5647 dry-run path.
4. Only after those pass, repeat the existing observed bounded powered test.

## Learning topics

- `ament_cmake` and `ament_cmake_python`
- ROS 2 C++ (`rclcpp`) publishers, subscriptions, services, timers, and QoS
- RAII cleanup for GPIO resources
- Separating pure control logic from ROS adapters

## Sources

- Existing repository implementation and local operating documentation.
- ROS 2 Jazzy headers and build tools installed in the lab Distrobox.
- libgpiod 1.6.3 headers installed from Ubuntu Noble universe.
