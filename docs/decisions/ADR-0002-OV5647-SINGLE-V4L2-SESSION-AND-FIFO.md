# ADR-0002: Use One V4L2 Session and a FIFO for FFmpeg

- Status: Accepted
- Date: 2026-08-23

## Context

The vendor pipeline selection performed by `VIDIOC_S_INPUT` is tied to the lifetime of the open `v4l2-ctl` process. A second process may attempt STREAMON after the first process has already closed the pipeline. Also, `v4l2-ctl` can emit status text on stdout, corrupting raw NV12 sent directly to FFmpeg.

## Decision

1. Execute input selection, format configuration, and capture in one `v4l2-ctl` process.
2. Send raw frames to a named FIFO or regular file through `--stream-to=<path>`.
3. Let FFmpeg read the FIFO/file instead of consuming `v4l2-ctl` stdout directly.

## Evidence

Separate processes produced sensor register-write and pipeline stream errors. Direct stdout piping produced a 45-byte corrupt packet matching the input-selection status text. The FIFO pipeline successfully delivered video.

## Consequences

- Capture wrappers must treat the V4L2 device lifetime as one transaction.
- The HTTP server creates a private FIFO for each single allowed client.
- Parallel camera sessions are rejected.

