"""
examples/record_dataset.py
===========================
Programmatic dataset recording without the dashboard UI.
Useful for automated data collection pipelines.

Usage
-----
    python examples/record_dataset.py \
        --repo-id your-username/my-dataset \
        --task "Pick up the cup and place it in the bowl" \
        --episodes 50

Requirements
------------
    pip install -e .
    # Plus LeRobot installed from source
"""
import argparse
import time

import requests

BASE = "http://localhost:7860/api"


def api(path: str, body: dict | None = None):
    url = BASE + path
    if body is not None:
        r = requests.post(url, json=body, timeout=30)
    else:
        r = requests.get(url, timeout=10)
    r.raise_for_status()
    return r.json()


def wait_for_phase(target_phases: list[str], timeout: float = 60.0) -> str:
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        d = api("/status")
        phase = d.get("phase", "unknown")
        if phase in target_phases:
            return phase
        time.sleep(0.3)
    raise TimeoutError(f"Timed out waiting for phase {target_phases}")


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--repo-id",   required=True, help="HuggingFace repo ID")
    p.add_argument("--task",      required=True, help="Task description")
    p.add_argument("--episodes",  type=int, default=50)
    p.add_argument("--fps",       type=int, default=30)
    p.add_argument("--ep-time",   type=int, default=22, dest="ep_time")
    p.add_argument("--reset-time",type=int, default=10, dest="reset_time")
    args = p.parse_args()

    print(f"Laundrobot — scripted recording")
    print(f"  Dataset  : {args.repo_id}")
    print(f"  Task     : {args.task}")
    print(f"  Episodes : {args.episodes}")
    print()

    # Connect arms (must already be plugged in and configured)
    print("Connecting arms...")
    d = api("/arms/connect")
    if not d.get("ok"):
        raise RuntimeError(f"Arm connect failed: {d}")
    print("Arms connected ✓")

    # Start teleoperation
    print("Starting teleoperation...")
    api("/teleop/start")
    print("Teleop running — ready to record")
    print()

    for ep in range(args.episodes):
        print(f"Episode {ep + 1}/{args.episodes} — press Enter when ready to record...")
        input()

        api("/record/start", {
            "repo_id":        args.repo_id,
            "task":           args.task,
            "num_episodes":   args.episodes,
            "fps":            args.fps,
            "episode_time_s": args.ep_time,
            "reset_time_s":   args.reset_time,
            "push_to_hub":    False,
        })
        print(f"  ⏺ Recording... ({args.ep_time}s)")
        wait_for_phase(["resetting", "connected", "done"], timeout=args.ep_time + 15)

        print(f"  ✓ Episode {ep + 1} done — saving...")
        api("/record/save_episode")
        wait_for_phase(["connected", "resetting"], timeout=30)
        print(f"  Saved. Resetting... ({args.reset_time}s)")
        time.sleep(args.reset_time)

    print()
    print(f"All {args.episodes} episodes recorded.")
    print(f"Push to Hub from the dashboard Dataset tab, or run:")
    print(f"  python -m lerobot.scripts.push_dataset_to_hub --repo-id {args.repo_id}")


if __name__ == "__main__":
    main()
