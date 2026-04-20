# Hardware Setup Guide

## Bill of Materials

| Qty | Part | Notes |
|---|---|---|
| 1–2 | SO-101 Follower Arm | The robot arm(s) being controlled |
| 1–2 | SO-100 Leader Arm | Operator arm(s) for teleoperation |
| 1–3 | USB Webcam | V4L2-compatible (Logitech C920 recommended) |
| 1 | Host Computer | Raspberry Pi 5 / Jetson Orin / x86 laptop |
| — | USB-A to USB-C cables | One per arm |
| — | USB hub (optional) | If the host has fewer than 4 USB ports |

## USB Port Mapping

Each arm appears as a `/dev/ttyACM*` device when plugged in. The number suffix is assigned by the kernel in plug-in order — it can change between reboots. For stable naming, install udev rules:

```bash
sudo ./scripts/setup_udev.sh
```

This creates persistent symlinks:
```
/dev/laundrobot-follower1  →  /dev/ttyACM0
/dev/laundrobot-follower2  →  /dev/ttyACM1
/dev/laundrobot-leader1    →  /dev/ttyACM2
```

## Finding your port assignments

```bash
# List all serial devices
ls -la /dev/ttyACM*

# Check which device is which (plug/unplug one at a time)
dmesg | grep ttyACM | tail -10

# Or use our helper script
./scripts/check_ports.sh
```

## Camera setup

```bash
# List all video devices
ls /dev/video*

# Check supported formats and resolutions for a camera
v4l2-ctl --device=/dev/video0 --list-formats-ext

# Recommended resolutions and their max FPS
# 640×480   → 30fps
# 1280×720  → 10–15fps
# 1920×1080 → 5–10fps
```

Use the **↻ Scan** button in the dashboard to auto-detect cameras.

## Camera placement

For consistent episode quality:
- Mount cameras on a fixed rig (not free-standing)
- Overview camera: ~60–80cm above the workspace, angled 30–45° down
- Wrist camera: mounted to the arm, pointed at the gripper
- Use the same physical setup for every recording session

## Recommended wiring order

1. Plug in **Follower 1** → becomes `/dev/ttyACM0`
2. Plug in **Follower 2** (if used) → becomes `/dev/ttyACM1`
3. Plug in **Leader** → becomes `/dev/ttyACM2`
4. Plug in cameras
5. Install udev rules to lock in these assignments permanently

## Power

SO-101 arms draw up to 2A per arm at 12V. Use the supplied power adapters — do not run from USB bus power.

## Troubleshooting

**`[TxRxResult] Port is in use!`**
Multiple threads are accessing the same serial port. This should never happen with Laundrobot's bus-ownership system. If you see it, check that no other program (e.g. a stray Python script) is also talking to the robot.

**Arm twitches on connect**
Normal — the arm initializes to the calibrated home position on first connect. Set a safe home position and always connect the arm with it in a neutral pose.

**Camera stream not appearing**
- Check the device path in the left config panel
- Run `./scripts/check_cameras.sh` to confirm the device exists
- Ensure no other program (e.g. `cheese`, `guvcview`) has the camera locked
