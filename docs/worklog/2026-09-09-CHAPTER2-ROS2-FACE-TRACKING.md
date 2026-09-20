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

## Follow-up: Orange Pi deployment readiness

On 2026-09-09, a read-only SSH inspection confirmed that the user cloned
`ros-packages` into `/root/ros2_ws/src/ros-packages`. The clone was clean on
`main` at `817b8f8` (`doc: add descriptions`) and matched `origin/main`.
`colcon list` discovered `lab_camera`, `lab_face_tracking`, `lab_interfaces`,
and `lab_stepper`, plus the user's separate `lab_examples` package. An existing
`/root/ros2_ws/install/local_setup.bash` was present, but this follow-up did not
assume that it was built from the current commit.

The board has `ros-jazzy-ros-base`, `ros-jazzy-cv-bridge`,
`python3-opencv`, and `python3-libgpiod`. The first inspection incorrectly
reported `opencv-data` as installed because a multi-package `dpkg-query -W`
line with an empty version was misread; the follow-up below corrects this.
`/dev/video8`,
`/dev/media0`, and `/dev/gpiochip0` exist. No actual camera capture process was
running during inspection. NTP synchronization was active. The board exports
`ROS_AUTOMATIC_DISCOVERY_RANGE=SUBNET`; no explicit `ROS_DOMAIN_ID` was observed.

The laptop's Ubuntu Jazzy Distrobox has `rqt_image_view`, shares the host network
address `192.168.1.173/24`, and also exports
`ROS_AUTOMATIC_DISCOVERY_RANGE=SUBNET`. The Orange Pi remains at the recorded
`192.168.1.236`. A VPN interface was present on the laptop, so DDS discovery
must be verified rather than inferred from matching subnet settings.

No build, package installation, device access, service start, camera capture,
GPIO request, or motor movement was performed in this follow-up. The immediate
procedure is: rebuild from the current clone; run a bounded camera check; start
the existing MJPEG server; launch all four ROS nodes with `dry_run:=true`; verify
the ROS graph and `/face/image` from the laptop; only then schedule the separate
eight-half-step powered experiment documented above.

## Follow-up: missing Haar cascade on Orange Pi

On 2026-09-10, the user's first Orange Pi launch started all four processes,
then `face_detector` exited because
`/usr/share/opencv4/haarcascades/haarcascade_frontalface_default.xml` was absent.
The launch system correctly stopped the camera bridge, controller, and dry-run
stepper after the required detector exited. The stepper log confirmed
`dry_run=True; DISARMED`; no GPIO or motor motion was involved.

A read-only SSH check observed:

- `dpkg-query -s opencv-data`: package is not installed;
- `apt-cache policy opencv-data`: Noble arm64 candidate
  `4.6.0+dfsg-13.1ubuntu1` from `ports.ubuntu.com`, component `universe`;
- no frontal-face Haar/LBP cascade XML under `/usr` or `/opt/ros/jazzy`.

Conclusion: install the explicitly documented Ubuntu `opencv-data` prerequisite
on the Orange Pi, verify the XML path, and rerun the same dry-run launch. A
workspace rebuild is unnecessary because the missing artifact is runtime data,
not compiled or generated ROS code. This follow-up did not install packages or
run camera/GPIO operations.

## Follow-up: real camera and laptop GUI validation

After installing `opencv-data`, the user reran the bounded 300-frame launch on
the Orange Pi. All four nodes started and the detector loaded
`/usr/share/opencv4/haarcascades/haarcascade_frontalface_default.xml`.
`rqt_image_view` in the laptop's Jazzy Distrobox displayed `/face/image` from
the OV5647, including the detector's red image-centre line. This directly
validates image transport from the board to the laptop through ROS 2 DDS.

Codex repeated the same bounded launch over SSH with `ROS_DOMAIN_ID=42`,
`ROS_AUTOMATIC_DISCOVERY_RANGE=SUBNET`, `with_stepper:=true`, and
`dry_run:=true`. It completed with exit 0: 300 images were published and 667
newer incoming JPEG frames superseded older queued frames. The camera node then
exited normally and launch sent SIGINT to the other three nodes; all exited
cleanly. The stepper remained `DISARMED` and simulated, so this experiment did
not request GPIO or move the motor.

The supplied screenshot shows part of a person but no mostly frontal face, so
absence of a face rectangle in that frame is expected for the Haar baseline and
does not indicate an image transport failure. The next experiment should first
place a well-lit frontal face in view and inspect `/face/target`, then exercise
explicitly armed dry-run motion before any bounded real-GPIO run.

## Follow-up: laptop custom-message decoding

The laptop command `ros2 topic echo /face/target` reported
`lab_interfaces/msg/FaceTarget is invalid`. Read-only inspection inside the
`ros-jazzy` Distrobox found the source link at
`/home/artm1904/ros2_ws/src/ros-packages`, and `colcon list` discovered all four
packages, but `/home/artm1904/ros2_ws/install` did not exist. With only
`/opt/ros/jazzy` sourced, `ros2 pkg prefix lab_interfaces` correctly reported
`Package not found`.

Conclusion: DDS discovery already works, but the laptop cannot deserialize a
custom message definition that has never been built into or sourced from its
environment. Build `lab_interfaces` locally for x86_64, source the resulting
overlay, verify it using `ros2 interface show`, then echo `/face/target` with
best-effort reliability to match the publisher. No Orange Pi rebuild or code
change is required for this runtime setup issue.

On 2026-09-16 the user built `lab_interfaces` successfully in the laptop
Distrobox. A follow-up inspection verified the installed prefix at
`/home/artm1904/ros2_ws/install/lab_interfaces`, displayed the complete
`FaceTarget` definition, and observed one live best-effort publisher from
`/face_detector`. A bounded laptop command then decoded one message successfully:
`detected=false`, dimensions 1280×720, frame `camera_optical_frame`. This closes
the custom-message setup issue. The false detection value only reports that no
face was found in that particular frame.

## Follow-up: laptop image-view latency

The user reported a very large delay while `rqt_image_view` subscribed to raw
`/face/image`. Live inspection showed that this topic is a 1280×720 BGR8 image,
2,764,800 bytes (2,700 KiB) per message. A best-effort laptop probe received
only 6 raw frames during a 10-second window, with measured header delay of
534–694 ms. This rate is too low for responsive viewing and can create visible
queue/backlog effects in GUI/network layers.

The explicit `/face/image/compressed` publisher carried approximately 70 KiB
JPEG frames in the same scene, about 39 times smaller. A following 10-frame
probe measured 346–492 ms header delay and completed promptly. The first delay
probe accidentally labelled microseconds as milliseconds; this report retains
the corrected millisecond measurements. A midpoint SSH clock comparison was
too sensitive to connection setup delay to improve these figures; both hosts
reported NTP synchronization.

Orange Pi inspection during the continuous dry-run also found high compute
load: `face_detector` approximately 245% CPU, FFmpeg approximately 120%, and
the high-frequency dry-run stepper timer approximately 41% at that instant.
These are contextual snapshots rather than sustained benchmarks. The direct
cause of the laptop GUI throughput problem is the raw image size; CPU use is a
remaining optimization target before powered closed-loop tracking.

The installed Jazzy `rqt_image_view` source confirms that a dropdown entry
ending in `/compressed` selects the `compressed` image-transport hint and uses
the sensor-data QoS profile. Therefore the selected remedy is to view
`/face/image/compressed` over Wi-Fi. No camera, GPIO, service, or source-code
change was made during these diagnostics.

The first attempt to select that entry exposed a separate laptop dependency
issue. RQt reported that `image_transport/compressed_sub` did not exist and
listed only `image_transport/raw_sub`. This directly shows that the compressed
subscriber plugin is absent from the Ubuntu Distrobox; it is not an Orange Pi
publisher or DDS discovery failure. Install
`ros-jazzy-compressed-image-transport` inside that Distrobox, close and restart
RQt after sourcing `/opt/ros/jazzy/setup.bash` and the workspace overlay, then
select `/face/image/compressed` again. Installation and the resulting GUI
latency remain to be verified by the user.

The user then verified that `ros2 pkg prefix compressed_image_transport`
resolved to `/opt/ros/jazzy`. Starting RQt with
`/face/image/compressed` as a positional argument failed, however, with an
image-transport warning followed by an incompatible-type subscription error.
Inspection of the Jazzy RQt source explains the result: a dropdown item stores
`/face/image compressed` internally, splits it into base topic and transport,
and asks `image_transport` to subscribe with the compressed hint. A literal
positional `/face/image/compressed` has no separator in its item data, so RQt
defaults it to the raw transport and attempts a `sensor_msgs/Image`
subscription on a topic whose real type is `sensor_msgs/CompressedImage`.

The earlier recommendation to pass `/face/image/compressed` positionally was
therefore incorrect. The corrected procedure is to start `rqt_image_view`
without an argument, refresh the topic list, and choose
`/face/image/compressed` from the dropdown. This correction is based on the
reported runtime error and lines 203–328 of the Jazzy source; GUI validation is
still pending.

Starting without an argument then reproduced the same immediate failure. This
is consistent with RQt restoring the previously saved literal topic during
`restoreSettings`, rather than evidence of a failed plugin installation. The
targeted recovery is to start once with the valid positional base topic
`/face/image`, which suppresses restoration of the stale setting, then select
the compressed entry in the GUI and exit normally. `rqt --clear-config` is a
broader fallback, but it also resets unrelated RQt layout and plugin settings.
The recovery remains to be run and validated on the laptop.

## Follow-up: staged ROS stepper preflight

On 2026-09-16, live Orange Pi inspection reconfirmed kernel
`6.6.98-vendor-sun60iw2`, Python 3.12.3, python-gpiod 1.6.3, and the expected
GPIO offsets 141, 99, 38, and 100. All four lines initially had no consumer,
and no ROS nodes were running. The first SSH command failed locally because
`/etc/ssh/ssh_config.d/20-systemd-ssh-proxy.conf` had unsafe ownership or
permissions; using `ssh -F /dev/null` bypassed that unrelated workstation
configuration without changing either host.

`EXP-ROS-MOTOR-001` ran the ROS stepper with `dry_run:=true`, rate limit 40
half-steps/s, travel limits ±8, and session budget 8. After explicit enable, one
fresh positive-rate command advanced the simulation to exactly 8 estimated
half-steps. Status then reported `enabled=false`, `session_steps=8`,
`coils_active=false`, and `reason=session_limit`. The process was explicitly
stopped and all GPIO lines remained unclaimed. This validates arming, timestamp
acceptance, scheduling, the session bound, automatic disarm, and status without
requesting GPIO.

`EXP-ROS-MOTOR-002` used the same limits with `dry_run:=false`, but sent no
motion command. Explicit enable successfully requested the lines as inactive
outputs; status remained at zero position and zero session steps with coils
inactive. Explicit disable released the request, and post-exit `gpioinfo`
reported every line `unused`. The kernel retained their output direction after
release, which is an observed pin state rather than an active libgpiod
consumer. No physical movement was commanded or claimed.

Direct SIGINT of the installed Python entry point produced an `rclpy` invalid
context traceback during executor shutdown. Its `finally` cleanup still ran,
the script exited, and the GPIO requests were released. This shutdown-log issue
should be investigated separately; it did not invalidate the zero-motion
result. Powered movement remains pending an operator who can see the motor and
immediately disconnect its supply.

After the operator confirmed readiness, `EXP-ROS-MOTOR-003` attempted to send
the bounded powered script over SSH. The SSH TCP connection timed out before
the remote script began, so no node launch, GPIO request, enable call, or motion
command from this experiment occurred. Three subsequent ICMP probes also
received no replies, while the laptop still routed `192.168.1.236` directly over
`wlan0` from `192.168.1.173`. The Orange Pi had been reachable after the prior
zero-motion cleanup, so the reason for the later loss of connectivity is
unverified. In accordance with the hardware runbook, the operator was told to
disconnect motor 5 V and inspect board power indicators before any retry.

On 2026-09-19 the user reported that Orange Pi connectivity was repaired.
Read-only verification found the board reachable at the same address, running
for approximately 1 hour 36 minutes after a reboot, with no ROS motor process
and all four GPIOs unclaimed inputs. A filtered current-boot kernel log showed
SD/MMC tuning timeout messages but no evidence establishing the motor supply as
the earlier network-loss cause. The post-reboot real-GPIO zero-motion test then
passed again: enable remained at zero steps with coils inactive, explicit
disable succeeded, and all four line consumers were released. Powered movement
still requires confirmation that the separately disconnected motor supply has
been restored under operator control.

After the operator confirmed that motor 5 V was on, the motor was visible, and
the disconnect was available, `EXP-ROS-MOTOR-004` executed the powered bounded
test. The real-GPIO node used a 40 half-step/s rate limit, estimated travel
limits ±8, and an eight-step total session budget. One fresh positive-rate
command produced status `estimated_half_steps=8`, `session_steps=8`,
`enabled=false`, `coils_active=false`, and `reason=session_limit`. Explicit
disable succeeded, the process exited, and all four GPIO lines again showed no
consumer. A postflight SSH check passed, no motor process remained, and the
filtered two-minute kernel log contained no matching power, thermal, watchdog,
reset, error, or failure message. This validates the software/GPIO bound and
cleanup. Physical rotation quality and direction await the operator's direct
observation; software counters are not shaft feedback.

The operator then reported that the test worked correctly and that the motor
and attached camera moved to the right. This completes the physical acceptance
of `EXP-ROS-MOTOR-004` and maps positive half-step rate to camera-right motion
for the current wiring and mount. Because normalized image error is positive
for a face right of centre, the current pan-controller `direction: 1` has the
expected corrective polarity for an unmirrored image. The experiment was a
manual bounded `StepperCommand`; automatic camera-to-face closed-loop behavior,
latency stability, steps per output revolution, and sustained thermal/load
operation remain unverified.

The documented next experiment is now a bounded automatic loop with the vision
launch and motor node kept as separate processes. The vision side runs for 300
frames without its embedded stepper, while the separately launched driver uses
±16 estimated-half-step travel limits and a 16-step session budget. This layout
allows a complete dry-run rehearsal and then a powered repeat by changing only
`dry_run`, while retaining explicit arming and disarming. Continuous powered
tracking remains deferred until compute load, latency, physical travel, and
thermal behavior are measured.

During the user's first powered automatic attempt, the live graph was complete:
detector → controller and controller → stepper each had compatible best-effort
publisher/subscriber endpoints. The stepper status showed that it had already
executed all 16 allowed transitions, ending at estimated position +12 with
`enabled=false`, inactive coils, and `reason=session_limit`. Thus the motor had
accepted automatic commands and stopped at its designed lifetime bound.

At the same time, `/face/target` reported `detected=false` and `/pan/command`
reported 0.0. An eight-second sample contained only false detections. A captured
81,830-byte `/face/image/compressed` frame showed an empty sofa with the centre
line and no person or face rectangle. The immediate no-motion observation is
therefore explained by both an exhausted motor session and absent current face
detection, not by a DDS or GPIO failure. A fresh real motor process must not be
started until RQt visibly shows a red face rectangle and a one-shot target
message reports `detected=true`.

When the user briefly moved their face toward the camera, one sampled target
reported `detected=true` at normalized x = -0.7875. A newly started bounded
motor process consequently reached -16 estimated half-steps and its session
limit. A following six-second correlation sample received 27 target messages
and 74 controller commands, but zero detections and zero nonzero commands. A
second captured annotated frame again showed the empty sofa and no person.
This confirms that the control response occurs when a face is detected, while
the present obstacle is keeping a frontal face continuously inside the actual
camera field of view—not motor communication.

The next live sample, with the user remaining in frame, was stable: all 57 of
57 target messages detected a face, normalized x ranged from -0.466 to -0.422,
and all 121 controller commands were nonzero negative rates from -25.25 to
-21.75 half-steps/s. The exhausted real motor node was explicitly disabled and
stopped. A fresh 16-step dry-run node then exercised the complete automatic
detector → controller → stepper path, reached exactly -16 simulated half-steps,
automatically disarmed for `session_limit`, and left GPIO unclaimed. A further
real run is intentionally paused for an operator clearance check because every
new process resets estimated zero while the mechanism has no homing or physical
position feedback.

After the operator confirmed approximately 30–40 degrees of clearance in both
directions, a gated powered experiment waited up to 60 seconds while the motor
node remained disarmed. It required ten consecutive detections outside a 0.20
normalized deadband with consistent sign. The gate passed at average x=-0.652,
then the script explicitly enabled a real-GPIO node bounded to ±16 estimated
half-steps, 16 total session steps, and 40 half-steps/s. After five seconds, the
one-shot status subscriber timed out and the shell exited with code 124, which
triggered its fail-closed trap. Postflight inspection found no stepper process
or node, all four GPIO lines had no consumer, SSH remained available, and the
immediate filtered kernel log was quiet. The recurring direct-SIGINT `rclpy`
invalid-context traceback appeared during shutdown. Physical motion and
direction from this gated run await the operator's observation; the missing
final status means the exact software step count is not claimed here.

The user then asked for unrestricted rotation because no camera movement was
visible. Unlimited motion was not enabled: without an encoder, homing switch,
or absolute position, removing travel/session bounds could wind the camera
cable or drive the mount into a stop. Instead, a larger isolated diagnostic
remapped the real stepper subscription to `/pan/manual_command`, preventing the
running pan controller's zero messages from cancelling the test. With ±64
travel limits, a 64-step session budget, and a refreshed +40 half-step/s
command, status recorded 60 real scheduled transitions before command timeout,
then explicit cleanup released every GPIO consumer. Physical movement from
this diagnostic awaits the operator's observation. If absent, the remaining
fault domain is downstream of the software scheduler: motor supply, common
ground, ULN2003 board/LEDs, wiring, or mechanics.

The user reported no movement during the 60-transition isolated test. A final
slow diagnostic then issued eight real half-steps at 2 half-steps/s while
sampling `/sys/kernel/debug/gpio` every 0.2 seconds. The kernel trace directly
showed consumer `ros2-lab-stepper` and the expected walking one-/two-phase
high/low pattern across offsets 141, 99, 38, and 100. Status reached exactly
eight estimated/session steps, automatically disarmed for `session_limit`, and
postflight showed all consumers released. This rules out ROS delivery,
scheduling, line ownership, and logical GPIO state for the no-motion symptom.
Do not remove bounds; power down before checking the separate 5 V supply,
common ground, ULN2003 LEDs and signal wiring, motor plug, and mechanics.

At the user's request, a larger isolated powered test used ±200 travel limits,
a 200-step session budget, and continuously refreshed +40 half-step/s commands.
It reached exactly `estimated_half_steps=200` and `session_steps=200`, then
automatically disarmed for `session_limit`, reported coils inactive, and
released all GPIO consumers. For a common 4096-half-step output revolution this
would be about 17.6 degrees, but the actual gearbox remains unmeasured. Physical
movement and ULN2003 LED behavior await the user's direct observation.

The operator confirmed that this 200-step run visibly moved the attached camera
to the right. This revalidates positive/right polarity and the full physical
path from ROS command through GPIO and ULN2003 to the mechanism. The earlier
16- and 60-step runs were below the operator's visible-motion threshold rather
than evidence of a failed driver. A 200-step session is now the bounded starting
scale for the next observed automatic tracking experiment; unrestricted motion
remains inappropriate without homing and position feedback.

On 2026-09-20 the user reported successful operation with the real driver set
to max rate 120, estimated travel ±600, and a two-million-transition session
budget, then asked about more speed. Live parameters showed the stepper at 120
but the automatic pan controller still at max rate 40 and gain 80. Face tracking
was therefore controller-limited; changing only the driver ceiling could not
make it exceed 40. The live node was still enabled with 407 accumulated steps,
a zero command, and inactive coils. It was explicitly disarmed; the service
confirmed output release and all GPIO consumers disappeared.

With normalized error limited to one and deadband 0.15, gain 80 cannot request
more than 68 even if the controller ceiling is raised. The guide now recommends
staged controller/driver tuning up to an observed 120 test while retaining
bounded sessions. Two million reversible transitions are inappropriate without
homing, limit switches, position feedback, measured steps per degree, and
thermal characterization. The source hard cap is 200 half-steps/s; this is a
scheduler validation limit, not a guarantee of reliable loaded motor speed.

After the complete loop worked at controller gain 160 and controller/driver
max rate 120, a dedicated clear-start runbook was added at
`docs/runbooks/ROS2_FACE_TRACKING_ORANGE_PI.md`. It covers one-time dependency
installation/build, environment setup in each terminal, stale-process/GPIO
preflight, camera service startup, face validation, separately bounded motor
startup, explicit arming, monitoring, shutdown, laptop compressed viewing,
troubleshooting, and command-option definitions. The canonical YAML defaults
were aligned with the validated controller and travel values: gain 160, rates
120, travel ±600. The user-tested two-million-transition session value was not
adopted; the repository and runbook use 1200 to limit supervised reversals.

No package was installed and the new instructions were not replayed from an
actual reboot during this documentation change. The running Orange Pi motor
node was observed still armed with 2,187 accumulated steps and a zero command;
it was explicitly disarmed, and GPIO ownership was verified released before
writing the procedure. Local validation parsed the updated YAML, checked every
local Markdown link in the new/modified entry-point documents, and passed
`git diff --check` in both the superproject and `ros-packages`. A ROS rebuild
was not run because no executable source changed.

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
- [Jazzy compressed_image_transport documentation](https://docs.ros.org/en/jazzy/p/compressed_image_transport/)
- [Jazzy rqt_image_view transport selection](https://github.com/ros-visualization/rqt_image_view/blob/jazzy/src/rqt_image_view/image_view.cpp)
