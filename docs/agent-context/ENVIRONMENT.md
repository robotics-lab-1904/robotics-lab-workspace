# Lab Environment

Last repository-layout verification: 2026-08-30. Hardware facts were last
verified from active work on 2026-08-23; re-verify them before use.

## Local workstation

- Workspace root: `/home/artm1904/Program/Robot/robotics-lab-workspace`
- Primary purpose: embedded Linux, robotics, ROS 2, camera, NPU, MCU, electronics, and algorithm experiments.
- The workspace is a Git superproject with four pinned submodules. Check the
  repository root and submodule status before Git operations.

```bash
git rev-parse --show-toplevel
git status --short --branch
git submodule status --recursive
```

## Single-board computer

| Property | Known value |
|---|---|
| Board | Orange Pi Zero 3W |
| Vendor platform | Allwinner `sun60iw2` (A733/T736 family) |
| Architecture | AArch64 |
| Distribution | Armbian, Ubuntu Noble package base |
| Kernel | `6.6.98-vendor-sun60iw2` |
| LAN address | `192.168.1.236` |
| SSH | `root@192.168.1.236` |
| SSH authentication | Interactive secret; never store it in this repository |

 

Verify a new session with:

```bash
uname -a
cat /etc/os-release
ip -brief address
lsblk
df -h
free -h
```

## Camera subsystem

| Property | Known value |
|---|---|
| Sensor | OmniVision OV5647, 5 MP |
| Interface | Two-lane MIPI CSI-2 |
| Vendor sensor name | `ov5647_2` |
| I2C/CCI controller | 9 |
| Sensor address | `0x36` 7-bit / `0x6c` Allwinner-style 8-bit |
| MCLK | MCLK2 |
| PWDN | PE10 |
| Video node | `/dev/video8` |
| Media node | `/dev/media0` |
| Module | `ov5647.ko` |

Data path:

```text
OV5647 → MIPI1 → CSI1 → TDM0 → ISP0 → scaler8 → /dev/video8
```

Installed camera utilities include V4L2 tools, FFmpeg, GStreamer, a snapshot viewer, bounded tests, and an MJPEG HTTP server. Confirm package versions before reporting them as current.

## Logging

Persistent systemd journal storage is configured with `Storage=persistent`.

```bash
journalctl --list-boots
journalctl -b 0
journalctl -b -1
journalctl -k -b 0
journalctl -k -b -1
```

The Armbian image may map `/var/log/journal` to `/var/log.hdd/journal`. Instantaneous power loss may still discard the final buffered records.

## Safety and uncertainty

- Network addresses, kernels, package versions, device nodes, and attached hardware are mutable facts.
- Verify live state instead of trusting this document blindly.
- The board is remotely accessible; avoid changes that can break boot without a tested rollback or physical recovery path.
