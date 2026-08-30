# OV5647 on Orange Pi Zero 3W

Detailed Russian build and troubleshooting guide:

[`OV5647_FULL_GUIDE_RU.md`](./OV5647_FULL_GUIDE_RU.md)

Target kernel: `6.6.98-vendor-sun60iw2` from https://github.com/orangepi-xunlong/linux-orangepi/tree/orange-pi-6.6-sun60iw2

## Active board configuration

- One OV5647 on the second CSI connector/path.
- Sensor node: `sensor2` (`ov5647_2`, CCI 9, address `0x6c`).
- Capture node: `/dev/video8`.
- `sensor0` and `vinc0` are disabled so the empty first CSI path is not probed.

The installed module is:

`/lib/modules/6.6.98-vendor-sun60iw2/kernel/bsp/drivers/vin/modules/sensor/ov5647.ko`

The active DTB is:

`/boot/dtb-6.6.98-vendor-sun60iw2/allwinner/sun60i-a733-orangepi-zero3w.dtb`

## Capture a PNG

On the board:

```sh
capture-ov5647 /tmp/ov5647.png
```

The helper selects video input 0, lets auto exposure settle for 30 frames,
captures 1280x720 NV12, and converts it to PNG.

## Local web viewer

Start the viewer on the board:

```sh
ov5647-web start
```

Open `http://192.168.1.236:8080/` in a browser. The page refreshes the camera
frame every two seconds. Control commands:

```sh
ov5647-web status
ov5647-web stop
ov5647-web restart
```

## Saved DTB variants on the board

- Original DTB: `sun60i-a733-orangepi-zero3w.pre-ov5647-20260811.dtb`
- Dual-OV5647 DTB: `sun60i-a733-orangepi-zero3w.dual-ov5647-20260811.dtb`

Do not install the dual variant again until the two-camera boot problem is
debugged with serial-console access.
