# OV5647 Camera Bring-up and Browser Streaming

## Objective

Add one OV5647 camera to the Orange Pi Zero 3W vendor camera stack, obtain stable frames, and expose an MJPEG stream in a browser.

## Environment

- Orange Pi Zero 3W
- Armbian / Ubuntu Noble
- Kernel `6.6.98-vendor-sun60iw2`
- OV5647 on the second CSI path
- `/dev/video8`, `/dev/media0`

## Result

The camera is detected as `ov5647_2`, bounded captures of 1, 10, 100, 1000, and 10000 frames succeeded, and continuous browser video works through an FFmpeg MJPEG pipeline.

Measured sustained capture:

```text
10000 frames
approximately 31.27 FPS
1280x720 NV12
1382400 bytes per frame
three cyclic DMA buffers
```

## Durable findings

### Three DMA buffers

Known-good capture uses:

```bash
--stream-mmap=3
```

Earlier unbounded attempts using four or tool-selected larger buffer counts coincided with severe failures. The sustained 10000-frame test with three buffers completed without DMA, IOMMU, panic, or watchdog errors.

### One V4L2 session

The Allwinner vendor stack closes its selected pipeline when the process that executes `--set-input=0` exits. Selection, format, and STREAMON must therefore occur in one `v4l2-ctl` command.

Incorrect pattern:

```bash
v4l2-ctl -d /dev/video8 --set-input=0
v4l2-ctl -d /dev/video8 --stream-mmap=3 --stream-count=100
```

Correct pattern:

```bash
v4l2-ctl -d /dev/video8 \
  --set-input=0 \
  --set-fmt-video=width=1280,height=720,pixelformat=NV12 \
  --stream-mmap=3 \
  --stream-count=100 \
  --stream-to=/dev/null
```

### Raw data isolation

When `--set-input=0` and `--stream-to=-` are combined, `v4l2-ctl` may write a human-readable status line to stdout before NV12. FFmpeg then sees a corrupt first packet. A named FIFO separates raw output from status output.

### Browser server

Installed paths:

```text
/usr/local/bin/ov5647-stream-server
/etc/systemd/system/ov5647-stream.service
/usr/local/bin/test-ov5647-stream
/usr/local/bin/test-ov5647-ffmpeg
```

The server:

- uses three DMA buffers;
- selects input and starts streaming in one process;
- sends raw NV12 through a named FIFO to FFmpeg;
- prevents concurrent camera clients;
- emits MJPEG over HTTP on port 8081;
- provides `/status.json` and an English debug panel;
- defaults to 25 output FPS.

## Important commands

```bash
test-ov5647-stream 10000
test-ov5647-ffmpeg 1000
ov5647-stream-server
```

Browser URL:

```text
http://192.168.1.236:8081/
```

## Logging

Persistent journald storage was enabled with a drop-in containing:

```ini
[Journal]
Storage=persistent
```

The default Armbian configuration had explicitly used `Storage=volatile`, so merely creating `/var/log/journal` was insufficient.

## Rejected hypotheses and corrections

- **External PSU failure:** changing the PSU did not eliminate the original behavior; later bounded tests showed the sensor and sustained pipeline were stable.
- **The 18:28 shutdown was a crash:** persistent journal showed a clean `systemd-logind` poweroff. The user confirmed this poweroff was intentional while changing the PSU.
- **FFmpeg corrupt packet indicated sensor corruption:** the corrupt packet was 45 bytes of `v4l2-ctl` status text mixed into stdout, not camera data.
- **Creating `/var/log/journal` enabled persistence:** rejected because Armbian explicitly set `Storage=volatile`; a configuration override was required.

## Known non-fatal messages

The vendor stack may report:

```text
v4l2 sub device scaler get_selection error
video8 has already stream off
```

These occurred around configuration/close while successful sustained captures completed. Continue monitoring them, but do not treat them as the root cause without additional evidence.

## Remaining work

- Validate service behavior across reboot before enabling autostart.
- Measure MJPEG CPU load, temperature, bitrate, latency, and Wi-Fi stability at 20, 25, and 30 FPS.
- Improve graceful shutdown so FFmpeg does not report a partial final raw frame after interruption.
- Update the longer camera guide with the final FIFO and debug-panel implementation.

