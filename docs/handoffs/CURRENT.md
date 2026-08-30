# Current Handoff

Last updated: 2026-08-30

## Current state

- A non-destructive Git migration runbook has been prepared for adding Armbian
  and the modified Orange Pi kernel as pinned submodules.
- The existing Armbian checkout has two uncommitted OV5647-related edits.
- The existing kernel checkout has three modified integration files and an
  untracked `ov5647.c`; these changes have not yet been committed or pushed.
- One OV5647 camera is operational on `/dev/video8`.
- A 10000-frame V4L2 test succeeded at approximately 31.27 FPS with three DMA buffers.
- FFmpeg MJPEG transfer works through a named FIFO.
- Browser streaming works on port 8081.
- The web UI includes an English debug panel backed by `/status.json`.
- Persistent journald storage is enabled.
- The systemd camera service is installed but should remain disabled until reboot behavior is validated.

## Next recommended work

1. Follow `docs/runbooks/GIT_SUBMODULE_AND_KERNEL_FORK.md`: create backups first,
   then create and publish the kernel fork branch.
2. Choose the Armbian preservation model: fork (recommended) or upstream
   submodule plus a versioned patch.
3. Add both submodules and validate them through a clean independent clone.
4. Restart the updated camera server and verify the debug panel after a hard browser refresh.
5. Measure actual FPS, bitrate, CPU load, temperature, and latency at 20, 25, and 30 output FPS.

## Stepper motor work pending on hardware

- An interactive ULN2003 controller supporting the board's libgpiod 1.6.3 and
  newer 2.x APIs is deployed under `/root/stepper-motor/`; all three local tests,
  traced dry-run, and live zero-motion GPIO request/release pass.
- Live pinctrl verified gpiochip0 offsets PE13=141, PD3=99, PB6=38, PD4=100 as
  unclaimed. The physical header mapping still originates from the user pinout.
- Start with 8 half-steps at 5 ms and stop on heat, unstable power, resets, or
  unexpected behavior. See the task report for the exact staged procedure.

## Constraints

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
