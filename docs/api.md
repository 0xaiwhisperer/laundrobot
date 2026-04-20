# Laundrobot API Reference

All endpoints are served by the Flask app running on the host machine.
Default base URL: `http://localhost:7860`

Requests with a body use `Content-Type: application/json`.
All responses are JSON unless noted.

---

## System

### `GET /api/status`
Full system status. Polled by the dashboard every 300ms.

**Response fields**

| Field | Type | Description |
|---|---|---|
| `phase` | string | Current phase: `idle`, `connected`, `teleop`, `recording`, `resetting`, `faiss`, `traj_play`, `traj_rec`, `countdown`, `done`, `error` |
| `arm_status` | object | `{follower, follower_2, leader}` booleans |
| `joints` | float[] | 6 joint angles for active arm (degrees) |
| `episode_num` | int | Current episode number |
| `saved_episodes` | int | Episodes saved this session |
| `loop_hz` | float | Control loop rate |
| `faiss_episode` | int\|null | Last FAISS matched episode |
| `faiss_dist_mm` | float\|null | Last FAISS match distance |
| `log` | object[] | Last N log entries `{ts, msg, level}` |

---

## Arms

### `POST /api/arms/connect`
Connect follower(s) and leader.

```json
{
  "follower_1_id": "follower",
  "follower_2_id": "follower_3"
}
```

### `POST /api/arms/disconnect`
Disconnect all arms (torque off first).

### `POST /api/arms/switch`
Hot-swap the active follower arm.

```json
{
  "port": "/dev/ttyACM1",
  "follower_1_cam":  "/dev/video0",
  "follower_1_cam2": "/dev/video4",
  "follower_2_cam":  "/dev/video2"
}
```

### `GET /api/arms/status`
Returns `{status: {follower, follower_2, leader}}` booleans.

---

## Teleoperation

### `POST /api/teleop/start`
Begin leader→follower teleoperation.

### `POST /api/teleop/stop`
Stop teleoperation.

---

## Recording

### `POST /api/record/start`
Start a dataset recording session.

```json
{
  "repo_id": "username/dataset-name",
  "task": "Pick up the cup and place it in the bowl",
  "num_episodes": 50,
  "fps": 30,
  "episode_time_s": 22,
  "reset_time_s": 10,
  "push_to_hub": false,
  "cam_device": "/dev/video0",
  "use_cam": true
}
```

### `POST /api/record/save_episode`
Save the current episode and start the reset timer.

### `POST /api/record/discard_episode`
Discard the current episode and re-record.

### `POST /api/record/stop`
End the recording session.

### `POST /api/home`
Send all connected arms to the saved home position. Works regardless of current state.

---

## Cameras

### `GET /stream?device=/dev/video0`
MJPEG stream for camera 1.

### `GET /stream2?device=/dev/video4`
MJPEG stream for camera 2.

### `GET /stream3?device=/dev/video2`
MJPEG stream for camera 3 (follower 2).

### `POST /api/cameras/scan`
Scan for available `/dev/video*` devices.

---

## FAISS Retrieval

### `POST /api/faiss/start`

```json
{
  "faiss_url":   "https://your-pod-5000.proxy.runpod.net",
  "faiss_url_2": "https://your-pod-3000.proxy.runpod.net",
  "faiss_mode":  "both",
  "task":        "Pick up the cup",
  "action_horizon": 10,
  "use_cam_3":   false
}
```

`faiss_mode`: `"both"` | `"follower_1"` | `"follower_2"`

### `POST /api/faiss/stop`
Stop FAISS retrieval.

### `POST /api/faiss/ping`
Check if FAISS server is reachable.

```json
{ "faiss_url": "https://your-pod-5000.proxy.runpod.net" }
```

---

## Animations

### `GET /animations`
Animation editor page (HTML).

### `GET /api/animation/list`
List saved animation files.

### `GET /api/animation/current`
Return the current in-memory animation.

### `GET /api/animation/status`
Playing state + current animation + post-FAISS setting.

### `GET /api/animation/observe`
Read live joint positions from both connected arms.

### `POST /api/animation/play`
Start animation playback.

```json
{
  "animation": { "name": "wave", "duration": 3.0, "arm1_keyframes": [...], "arm2_keyframes": [...] },
  "loop": false
}
```

### `POST /api/animation/stop`
Stop animation playback.

### `POST /api/animation/save`
Save current animation to disk.

```json
{ "name": "wave_greeting" }
```

### `POST /api/animation/load`
Load animation from disk.

```json
{ "filename": "wave_greeting.json" }
```

### `POST /api/animation/keyframe/add`
Add or replace a keyframe.

```json
{
  "arm": "arm1",
  "time": 1.5,
  "joints": { "shoulder_pan": 45.0, "shoulder_lift": -60.0, ... },
  "easing": "ease-in-out"
}
```

### `POST /api/animation/keyframe/delete`
Delete a keyframe by index.

### `POST /api/animation/record/start`
Begin motion-capture recording (disables torque automatically).

```json
{ "arms": { "arm1": true, "arm2": false }, "rate": 15 }
```

### `POST /api/animation/record/stop`
Stop recording.

### `POST /api/animation/record/apply`
Convert recorded samples to keyframes.

### `POST /api/animation/jog/enable`
Stop preview loop and enable live slider control.

### `POST /api/animation/jog/disable`
Re-enable preview loop.

### `POST /api/animation/jog`
Send joint positions to one arm immediately.

```json
{ "arm": "arm1", "joints": { "shoulder_pan": 30.0, ... } }
```

### `POST /api/animation/torque/on`
Enable torque on all connected arms.

### `POST /api/animation/torque/off`
Disable torque (arms go limp).

### `GET /api/animation/home`
Return saved home position.

### `POST /api/animation/home/set`
Save current slider values as home position.

```json
{
  "arm1": { "shoulder_pan": 0, ... },
  "arm2": { "shoulder_pan": 0, ... }
}
```

### `POST /api/animation/home/go`
Send all arms to saved home position immediately.

### `POST /api/animation/set_post_faiss`
Set which animation plays automatically after FAISS retrieval.

```json
{ "filename": "home_reset.json" }
```

### `POST /api/animation/preview_restore`
Restart the preview loop (called by `sendBeacon` on page unload).

---

## Trajectories

### `GET /api/traj/list`
List saved trajectory files.

**Response**
```json
{
  "trajectories": [
    { "name": "pick_cup", "filename": "pick_cup.json", "frames": 660, "duration_s": 22.0, "fps": 30, "ts": "2025-01-15 14:32" }
  ],
  "dir": "/home/user/laundrobot/trajectories"
}
```

### `GET /api/traj/status`
Current recording/playback state.

### `POST /api/traj/record/start`
Start trajectory recording (stops preview loop automatically).

```json
{ "fps": 30 }
```

### `POST /api/traj/record/stop`
Stop recording (restarts preview loop).

### `POST /api/traj/record/save`
Save recorded buffer to disk.

```json
{ "name": "pick_cup", "fps": 30 }
```

### `POST /api/traj/record/discard`
Discard recorded buffer.

### `POST /api/traj/play/start`
Play a saved trajectory.

```json
{
  "filename": "pick_cup.json",
  "speed": 1.0,
  "loop": false,
  "countdown_s": 0,
  "shake_amplitude": 0.0,
  "pause_interval_s": 0.0
}
```

### `POST /api/traj/play/stop`
Stop playback (restarts preview loop).

### `POST /api/traj/delete`
Delete a saved trajectory.

### `POST /api/traj/rename`
Rename a saved trajectory.

---

## Datasets

### `GET /api/dataset/list`
List all local LeRobot datasets.

### `POST /api/dataset/push`
Push a dataset to Hugging Face Hub.

```json
{ "repo_id": "username/dataset", "private": false }
```

### `POST /api/dataset/delete`
Delete a local dataset.
