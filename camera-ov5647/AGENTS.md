# OV5647 Camera Subsystem Instructions

These rules apply to work under `camera-ov5647/` and supplement the repository-root `AGENTS.md`.

## Required reading

Before changing or testing the camera stack, read:

- `../docs/runbooks/OV5647_CAMERA.md`
- `../docs/decisions/ADR-0001-OV5647-THREE-DMA-BUFFERS.md`
- `../docs/decisions/ADR-0002-OV5647-SINGLE-V4L2-SESSION-AND-FIFO.md`
- `../docs/worklog/2026-08-23-OV5647-CAMERA-BRINGUP.md`

## Known-good configuration

- Board: Orange Pi Zero 3W, Allwinner sun60iw2 vendor platform.
- Kernel: `6.6.98-vendor-sun60iw2`.
- Sensor: OV5647 on vendor sensor slot `ov5647_2`.
- Capture device: `/dev/video8`; media device: `/dev/media0`.
- Stable capture: `1280x720`, `NV12`, approximately 31.27 FPS.
- Use exactly three V4L2 MMAP buffers: `--stream-mmap=3`.
- Perform `--set-input=0`, format selection, and streaming in the same `v4l2-ctl` process.
- Do not pipe `v4l2-ctl` stdout directly to FFmpeg when `--set-input=0` is present; its status text corrupts raw NV12. Use a regular file or named FIFO via `--stream-to=<path>`.
- Never allow two processes or HTTP clients to open the camera concurrently.

## Test progression

Use the provided bounded tests before an unbounded stream:

```bash
test-ov5647-stream 1
test-ov5647-stream 10
test-ov5647-stream 100
test-ov5647-stream 1000
test-ov5647-stream 10000
test-ov5647-ffmpeg 100
test-ov5647-ffmpeg 1000
```

Do not enable service autostart until the current implementation has survived a reboot and a sustained test.

## Required evidence

After significant tests, capture relevant output from:

```bash
journalctl -k -b 0
journalctl -u ov5647-stream.service -b 0
media-ctl -d /dev/media0 -p
```

Record FPS, frame count, dropped frames, bitrate, CPU load, temperature, and any VIN/MIPI/IOMMU/DMA errors in the task report.

