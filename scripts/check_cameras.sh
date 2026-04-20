#!/usr/bin/env bash
# check_cameras.sh — list all connected V4L2 cameras with their capabilities
set -euo pipefail

echo "═══════════════════════════════════════"
echo "  Laundrobot — Camera Detection"
echo "═══════════════════════════════════════"
echo ""

devices=$(ls /dev/video* 2>/dev/null | grep -E '^/dev/video[0-9]+$' || true)

if [[ -z "$devices" ]]; then
  echo "No /dev/video* devices found."
  echo ""
  echo "Troubleshooting:"
  echo "  • Check USB connections"
  echo "  • Try: lsusb | grep -i camera"
  exit 1
fi

for dev in $devices; do
  echo "────────────────────────────────────────"
  echo "Device: $dev"
  if command -v v4l2-ctl &>/dev/null; then
    name=$(v4l2-ctl --device="$dev" --info 2>/dev/null | grep "Card type" | sed 's/.*: //' || echo "Unknown")
    echo "Name:   $name"
    echo ""
    echo "Supported formats:"
    v4l2-ctl --device="$dev" --list-formats-ext 2>/dev/null \
      | grep -E "(JPEG|YUYV|Size|Interval)" \
      | head -20 \
      || echo "  (install v4l-utils for detailed format info)"
  else
    echo "  (install v4l-utils for format info: sudo apt install v4l-utils)"
  fi
  echo ""
done

echo "═══════════════════════════════════════"
echo "Found devices: $devices"
echo ""
echo "Suggested Laundrobot config:"
echo "  Camera 1 (overview): first device above"
echo "  Camera 2 (wrist):    second device above"
echo "  Camera 3 (arm 2):    third device above"
