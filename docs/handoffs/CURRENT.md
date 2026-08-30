# Current Handoff

Last updated: 2026-08-30

## Current state

- `robotics-lab-workspace` is the active superproject at
  `/home/artm1904/Program/Robot/robotics-lab-workspace`.
- Four submodules are registered and pinned: camera, stepper motor, upstream
  Armbian build, and the Orange Pi kernel fork.
- The kernel submodule points to `robotics/ov5647-sun60iw2` at `4590a2f`.
- The Armbian customization is stored as
  `patches/armbian/0001-enable-ov5647-sun60iw2.patch`; the submodule remains an
  upstream checkout and becomes dirty only when this patch is applied.
- Internal Markdown navigation uses local relative links across superproject
  and submodule boundaries; the recursive superproject checkout is canonical.
- One OV5647 camera is operational on `/dev/video8`.
- A 10000-frame V4L2 test succeeded at approximately 31.27 FPS with three DMA buffers.
- FFmpeg MJPEG transfer works through a named FIFO.
- Browser streaming works on port 8081.
- The web UI includes an English debug panel backed by `/status.json`.
- Persistent journald storage is enabled.
- The systemd camera service is installed but should remain disabled until reboot behavior is validated.

## Next recommended work

1. Rotate the board SSH password because the previous credential existed in
   commit `5f5ac26`; deleting it from the current files does not remove it from
   Git history.
2. Commit and push documentation corrections in each changed submodule, then
   update and commit the corresponding superproject gitlink.
3. Validate the complete workspace through a clean `--recurse-submodules`
   clone and verify the Armbian patch with
   `bash patches/armbian/apply_patch.sh --check`.
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
