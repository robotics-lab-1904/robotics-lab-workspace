# OV5647 Camera Runbook

## Purpose

Safely verify and operate the OV5647 camera on the Orange Pi Zero 3W.

## Preconditions

- Power must be off while changing the CSI cable.
- Confirm the 22-contact cable orientation and seating.
- Confirm no capture process is active:

```bash
pgrep -af 'v4l2-ctl|ffmpeg|gst-launch|ov5647-stream-server'
```

## Verify detection

```bash
uname -r
ls -l /dev/video8 /dev/media0
lsmod | grep -E 'ov5647|vin_v4l2|vin_io'
dmesg | grep -Ei 'ov5647|sunxi:vin'
media-ctl -d /dev/media0 -p
```

Expected sensor ID evidence:

```text
[ov5647]detected chip id 0x5647
```

## Bounded capture

```bash
test-ov5647-stream 1
test-ov5647-stream 100
test-ov5647-stream 1000
```

For a long validation:

```bash
test-ov5647-stream 10000
```

## FFmpeg validation

```bash
test-ov5647-ffmpeg 100
test-ov5647-ffmpeg 1000
```

The test must use a named FIFO, not a direct stdout pipe.

## Browser stream

Foreground:

```bash
ov5647-stream-server
```

Systemd:

```bash
systemctl start ov5647-stream.service
systemctl status ov5647-stream.service
journalctl -fu ov5647-stream.service
```

Open:

```text
http://192.168.1.236:8081/
http://192.168.1.236:8081/status.json
```

## Stop

Foreground: press `Ctrl+C` once and wait for cleanup.

Systemd:

```bash
systemctl stop ov5647-stream.service
```

Confirm cleanup:

```bash
pgrep -af 'v4l2-ctl|ffmpeg|ov5647-stream-server'
```

## Diagnose a failure

```bash
journalctl -k -b 0 --since '20 minutes ago' --no-pager
journalctl -u ov5647-stream.service -b 0 --since '20 minutes ago' --no-pager
journalctl --list-boots
```

Search for:

```text
VIN_DEV_I2C_ERR
sensor write array error
__vin_pipeline_s_stream error
IOMMU fault
DMA timeout
watchdog
panic
```

Do not immediately retry an unbounded stream. Return to a one-frame bounded test and change one variable at a time.

## Rollback references

Saved DTB variants and camera artifacts are documented in `camera-ov5647/README.md`. Verify filenames and checksums on the board before replacing the active DTB.

