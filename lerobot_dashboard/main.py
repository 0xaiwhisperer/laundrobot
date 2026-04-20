"""
lerobot_dashboard/main.py — Laundrobot CLI entry point.

Usage
-----
    laundrobot --follower /dev/ttyACM0 --leader /dev/ttyACM2
    laundrobot --follower /dev/ttyACM0 --follower2 /dev/ttyACM1 --leader /dev/ttyACM2
    laundrobot --help
"""
from __future__ import annotations

import argparse
import sys


def _build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="laundrobot",
        description=(
            "Laundrobot — dual-arm robot teleoperation, animation, and "
            "data-collection studio built on LeRobot."
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples
--------
  # Single-arm setup
  laundrobot --follower /dev/ttyACM0 --leader /dev/ttyACM2

  # Dual-arm setup
  laundrobot --follower /dev/ttyACM0 --follower2 /dev/ttyACM1 --leader /dev/ttyACM2

  # Custom port, debug mode
  laundrobot --follower /dev/ttyACM0 --leader /dev/ttyACM2 --port 8080 --debug

Port mapping (default)
----------------------
  Follower 1  /dev/ttyACM0   Primary robot arm
  Follower 2  /dev/ttyACM1   Second arm (dual-arm setups)
  Leader      /dev/ttyACM2   Operator arm for teleoperation
        """,
    )

    # Arms
    p.add_argument("--follower",  default="/dev/ttyACM0", metavar="PORT",
                   help="Follower arm 1 serial port (default: /dev/ttyACM0)")
    p.add_argument("--follower2", default=None,           metavar="PORT",
                   help="Follower arm 2 serial port (dual-arm setups)")
    p.add_argument("--leader",    default="/dev/ttyACM2", metavar="PORT",
                   help="Leader arm serial port (default: /dev/ttyACM2)")

    # Calibration
    p.add_argument("--follower-id",  default="follower",   metavar="ID",
                   help="Calibration ID for follower 1 (default: follower)")
    p.add_argument("--follower2-id", default="follower_3", metavar="ID",
                   help="Calibration ID for follower 2 (default: follower_3)")

    # Cameras
    p.add_argument("--cam1",  default="/dev/video0", metavar="DEV",
                   help="Camera 1 device (default: /dev/video0)")
    p.add_argument("--cam2",  default="/dev/video4", metavar="DEV",
                   help="Camera 2 / wrist device (default: /dev/video4)")
    p.add_argument("--cam3",  default="/dev/video2", metavar="DEV",
                   help="Camera 3 / follower-2 device (default: /dev/video2)")

    # Server
    p.add_argument("--host",  default="0.0.0.0", metavar="HOST",
                   help="Host to bind to (default: 0.0.0.0)")
    p.add_argument("--port",  default=7860, type=int, metavar="PORT",
                   help="HTTP port (default: 7860)")
    p.add_argument("--debug", action="store_true",
                   help="Enable Flask debug mode (auto-reload on code changes)")

    return p


def main() -> None:
    parser = _build_parser()
    args   = parser.parse_args()

    # Lazy imports so --help is instant
    from .config import PORTS, RecordSession  # noqa: PLC0415

    # Populate port config from CLI args
    PORTS["follower"]   = args.follower
    PORTS["follower_1"] = args.follower
    if args.follower2:
        PORTS["follower_2"] = args.follower2
    PORTS["leader"] = args.leader

    # Populate default camera config
    sess = RecordSession()
    sess.cam_device   = args.cam1
    sess.cam_device_2 = args.cam2
    sess.cam_device_3 = args.cam3
    sess.follower_1_cam  = args.cam1
    sess.follower_1_cam2 = args.cam2
    sess.follower_2_cam  = args.cam3

    from .app import create_app  # noqa: PLC0415

    app = create_app()

    print()
    print("  ██╗      █████╗ ██╗   ██╗███╗  ██╗██████╗ ██████╗  ██████╗ ██████╗  ██████╗ ████████╗")
    print("  ██║     ██╔══██╗██║   ██║████╗ ██║██╔══██╗██╔══██╗██╔═══██╗██╔══██╗██╔═══██╗╚══██╔══╝")
    print("  ██║     ███████║██║   ██║██╔██╗██║██║  ██║██████╔╝██║   ██║██████╔╝██║   ██║   ██║   ")
    print("  ██║     ██╔══██║██║   ██║██║╚████║██║  ██║██╔══██╗██║   ██║██╔══██╗██║   ██║   ██║   ")
    print("  ███████╗██║  ██║╚██████╔╝██║ ╚███║██████╔╝██║  ██║╚██████╔╝██████╔╝╚██████╔╝   ██║   ")
    print("  ╚══════╝╚═╝  ╚═╝ ╚═════╝ ╚═╝  ╚══╝╚═════╝ ╚═╝  ╚═╝ ╚═════╝ ╚═════╝  ╚═════╝    ╚═╝  ")
    print()
    print(f"  Dashboard  →  http://localhost:{args.port}")
    print(f"  Animations →  http://localhost:{args.port}/animations")
    print()
    print(f"  Follower 1 : {args.follower}  (id: {args.follower_id})")
    if args.follower2:
        print(f"  Follower 2 : {args.follower2}  (id: {args.follower2_id})")
    print(f"  Leader     : {args.leader}")
    print(f"  Cameras    : {args.cam1}  {args.cam2}  {args.cam3}")
    print()

    try:
        app.run(host=args.host, port=args.port, debug=args.debug, threaded=True)
    except KeyboardInterrupt:
        print("\n  Laundrobot stopped.")
        sys.exit(0)


if __name__ == "__main__":
    main()
