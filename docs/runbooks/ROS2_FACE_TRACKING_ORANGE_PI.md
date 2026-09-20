# ROS 2 Face Tracking on the Orange Pi

## Purpose

Start the complete Chapter 2 adaptation after a reboot or from fresh terminals:

```text
OV5647 → MJPEG server → ROS camera bridge → face detector
       → pan controller → stepper driver → ULN2003 → camera mount
```

The current implementation detects and follows the largest frontal face. It
does not identify a person.

## Validated environment

- Orange Pi Zero 3W, Ubuntu 24.04 base, ROS 2 Jazzy
- OV5647 through the existing local MJPEG server
- ULN2003 on `/dev/gpiochip0`, offsets `[141, 99, 38, 100]`
- Positive motor command moves the camera right
- Validated controller values: gain 160, maximum rate 120 half-steps/s
- Validated visible manual movement: 200 half-steps at 40 half-steps/s

The mount has no encoder, homing switch, or physical limit switch. Every motor
process starts with estimated position zero regardless of the actual camera
angle.

## Safety preflight

Power down before changing CSI, GPIO, ULN2003, motor, ground, or supply wiring.
For powered operation:

- keep the camera mount visible;
- keep motor-power disconnect within reach;
- confirm cable clearance throughout the intended pan range;
- stop on vibration without rotation, heat, smell, supply instability, reset,
  or unexpected direction;
- do not run the motor from Orange Pi GPIO power.

Close browser tabs displaying `/stream.mjpg`. The camera server supports one
image client, which will be the ROS camera bridge.

## One-time workspace build

Run after a clean clone or any source/configuration change:

```bash
apt update
apt install -y libgpiod-dev python3-libgpiod opencv-data

source /opt/ros/jazzy/setup.bash
cd /root/ros2_ws

rosdep install \
  --from-paths src/ros-packages \
  --ignore-src \
  --rosdistro jazzy \
  -y

colcon build \
  --symlink-install \
  --executor sequential
```

Do not copy the laptop's `build/` or `install/` directories to the Orange Pi;
build separately for AArch64.

## Common environment for every Orange Pi terminal

Run these commands in every new terminal:

```bash
export ROS_DOMAIN_ID=42
export ROS_AUTOMATIC_DISCOVERY_RANGE=SUBNET
source /opt/ros/jazzy/setup.bash
source /root/ros2_ws/install/setup.bash
```

`ROS_DOMAIN_ID=42` isolates this lab graph from ROS nodes in other domains.
`SUBNET` permits discovery between the Orange Pi and laptop on the LAN.
The first `source` loads ROS 2 Jazzy; the second loads the lab packages.

## 1. Verify a clear starting state

```bash
pgrep -af 'chapter2.launch|mjpeg_camera|face_detector|pan_controller|stepper_node'
gpioinfo gpiochip0 | grep -E 'line +(38|99|100|141):'
```

Before starting, there must be no old `stepper_node`. Each GPIO line should
have no consumer. If `/pan/enable` exists from an old node, disarm it:

```bash
ros2 service call /pan/enable \
  std_srvs/srv/SetBool \
  '{data: false}'
```

Then stop the old node in its original terminal with `Ctrl+C`. Do not start two
nodes providing `/pan/enable`.

## 2. Start the OV5647 stream server

```bash
systemctl start ov5647-stream.service
systemctl --no-pager --full status ov5647-stream.service
curl -fsS http://127.0.0.1:8081/status.json
```

The service owns `/dev/video8` and publishes MJPEG at
`http://127.0.0.1:8081/stream.mjpg`. Do not open that stream in a browser while
ROS is using it.

## 3. Verify tracking configuration

The working values are stored in:

```text
/root/ros2_ws/src/ros-packages/lab_face_tracking/config/chapter2.yaml
```

Relevant section:

```yaml
pan_controller:
  ros__parameters:
    deadband: 0.15
    gain: 160.0
    max_rate: 120.0
    target_timeout: 0.5
    direction: 1
```

After editing this file, rebuild `lab_face_tracking`, source the workspace, and
restart the launch:

```bash
cd /root/ros2_ws
colcon build --symlink-install --packages-select lab_face_tracking
source /root/ros2_ws/install/setup.bash
```

## 4. Start camera, face detector, and controller

In **terminal 1**, load the common environment and run:

```bash
ros2 launch lab_face_tracking chapter2.launch.py \
  implementation:=cpp \
  source_url:=http://127.0.0.1:8081/stream.mjpg \
  with_stepper:=false \
  direction:=1 \
  max_frames:=0
```

`with_stepper:=false` is intentional. The real stepper is started separately
with explicit hardware limits. `max_frames:=0` permits continuous supervised
vision; use `max_frames:=600` for an approximately one-minute bounded run at the
configured 10 Hz.

## 5. Confirm face detection before motor startup

In **terminal 2**, load the common environment and run:

```bash
ros2 topic echo /face/target \
  --qos-reliability best_effort \
  --once

ros2 topic echo /pan/command \
  --qos-reliability best_effort \
  --once
```

Required before arming:

- `detected: true` repeats while the face remains visible;
- a face right of centre gives a positive command;
- a face left of centre gives a negative command;
- a centred face produces `half_steps_per_second: 0.0`.

Use a well-lit, mostly frontal face. On the laptop, RQt should show a stable red
face rectangle before powered tracking begins.

## 6. Start the real stepper, still disarmed

In **terminal 3**, load the common environment and run:

```bash
ros2 run lab_stepper stepper_node --ros-args \
  -p dry_run:=false \
  -p max_rate:=120.0 \
  -p min_position:=-600 \
  -p max_position:=600 \
  -p max_session_steps:=1200
```

The node starts **disarmed** and does not request GPIO until `/pan/enable` is
called. The command contains the package name `lab_stepper` followed by its
executable name `stepper_node`; ROS packages and executables may have different
names. `stepper_node` is the C++ implementation. Use `stepper_node_py` only when
deliberately testing the preserved Python implementation.

## 7. Arm and monitor automatic tracking

Place the face near the image centre first. In **terminal 2**:

```bash
ros2 service call /pan/enable \
  std_srvs/srv/SetBool \
  '{data: true}'

ros2 topic echo /pan/status
```

Move slowly left and right. The camera should pan toward the face and stop in
the centre deadband. It should also stop when the face disappears or becomes
stale.

Important status fields:

- `enabled`: whether the node can accept motion commands;
- `estimated_half_steps`: software-only position relative to process startup;
- `session_steps`: total transitions including reversals;
- `coils_active`: whether a phase is currently energized;
- `reason`: `tracking`, `zero_command`, `command_timeout`, `travel_limit`,
  `session_limit`, or `disarmed`;
- `fault`: GPIO or shutdown error, otherwise null.

## 8. Stop safely

Stop monitoring with `Ctrl+C`, then disarm before stopping processes:

```bash
ros2 service call /pan/enable \
  std_srvs/srv/SetBool \
  '{data: false}'
```

Expected response:

```text
success=True, message='Disarmed; outputs released'
```

Then:

1. Press `Ctrl+C` in terminal 3 to stop the stepper node.
2. Press `Ctrl+C` in terminal 1 to stop vision.
3. Optionally stop the camera server:

```bash
systemctl stop ov5647-stream.service
```

4. Switch off motor 5 V when the experiment is complete.
5. Confirm cleanup:

```bash
pgrep -af 'chapter2.launch|mjpeg_camera|face_detector|pan_controller|stepper_node'
gpioinfo gpiochip0 | grep -E 'line +(38|99|100|141):'
```

## Command option reference

### `chapter2.launch.py`

| Option | Meaning |
|---|---|
| `implementation` | `cpp` (default) runs the C++ nodes; `python` runs the preserved Python nodes with `_py` executable names. |
| `source_url` | MJPEG input. Use loopback because all processing runs on the Orange Pi. |
| `image_path` | Optional local JPEG fixture; skips the live HTTP camera. Never use it for powered tracking. |
| `max_frames` | Number of frames before launch shuts down. `0` means continuous. |
| `with_stepper` | Starts a stepper inside the launch. Keep `false` when using the separately bounded real node. |
| `dry_run` | Applies only to the stepper started by the launch. Default is `true`. |
| `direction` | `1` preserves current polarity; `-1` reverses controller commands. Current wiring uses `1`. |

### `lab_stepper/stepper_node`

| Option | Meaning |
|---|---|
| `dry_run` | `true` simulates outputs and never imports/requests GPIO; `false` uses real GPIO. |
| `max_rate` | Maximum accepted absolute command in half-steps/s. Source validation permits at most 200; reliable loaded speed may be lower. |
| `min_position` | Minimum estimated position relative to process startup. It is not an absolute measured angle. |
| `max_position` | Maximum estimated position relative to process startup. It is not an absolute measured angle. |
| `max_session_steps` | Total transition budget including both directions. Re-arming does not reset it. Restarting the process does. |
| `command_timeout` | Stops motion if no fresh command arrives; configured default is 0.5 seconds. |
| `chip` | GPIO character device, currently `/dev/gpiochip0`. |
| `offsets` | IN1–IN4 GPIO offsets, currently `[141, 99, 38, 100]`. |

### Controller parameters in `chapter2.yaml`

| Parameter | Meaning |
|---|---|
| `deadband` | Normalized horizontal region around centre where no movement is commanded. |
| `gain` | Converts horizontal error outside the deadband into half-steps/s. |
| `max_rate` | Controller command ceiling. The stepper ceiling must be equal or higher. |
| `target_timeout` | Rejects old face observations. |
| `direction` | Changes the sign of every command. Use `1` for the validated mount. |

The approximate controller law is:

```text
rate = min(max_rate, gain × (abs(horizontal_error) - deadband))
```

## Laptop image viewer

Use the same domain inside the Jazzy Distrobox:

```zsh
export ROS_DOMAIN_ID=42
export ROS_AUTOMATIC_DISCOVERY_RANGE=SUBNET
source /opt/ros/jazzy/setup.zsh
source ~/ros2_ws/install/setup.zsh
ros2 run rqt_image_view rqt_image_view
```

Select `/face/image/compressed` from the dropdown. Do not pass that compressed
topic as a positional argument. If an old invalid selection crashes RQt, start
once with the base topic:

```zsh
ros2 run rqt_image_view rqt_image_view /face/image
```

Then select `/face/image/compressed` in the GUI and close RQt normally.

## Troubleshooting

### Face visible but no motion

```bash
ros2 topic echo /face/target --qos-reliability best_effort --once
ros2 topic echo /pan/command --qos-reliability best_effort --once
ros2 topic echo /pan/status --once
```

- `detected: false`: improve pose, lighting, size, or field of view.
- command `0.0`: face is absent, centred, stale, or detection dropped.
- `enabled: false`, `reason: disarmed`: call `/pan/enable` after inspection.
- `reason: travel_limit`: physical/estimated travel limit was reached.
- `reason: session_limit`: stop and inspect; re-arming cannot reset the budget.

### Software counts steps but motor does not move

Power down before touching wiring. Check motor 5 V, shared ground, ULN2003
power and IN1–IN4 LEDs, signal order, motor plug, and mechanical binding. The
validated visible scale for this mount was 200 half-steps; very small movements
may not be visually apparent.

### Increase speed

Raise controller `max_rate` and `gain` together, with stepper `max_rate` equal
or higher. Validated advanced values are controller `max_rate=120`, `gain=160`,
and stepper `max_rate=120`. Do not jump directly to the source ceiling of 200;
watch for missed steps, stalls, supply sag, heat, and overshoot.

## Why the session remains bounded

`max_session_steps=2000000` was observed working, but it is not the recommended
operating value. Position limits prevent one-way estimated travel, while a
large session budget still allows prolonged reversal between the endpoints.
Use 1200 for supervised testing until the mount has measured steps per degree,
homing or physical limit switches, cable management, and thermal validation.
