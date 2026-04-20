#!/usr/bin/env bash
# check_ports.sh — list all connected serial devices (robot arms)
set -euo pipefail

echo "═══════════════════════════════════════"
echo "  Laundrobot — Serial Port Detection"
echo "═══════════════════════════════════════"
echo ""

devices=$(ls /dev/ttyACM* /dev/ttyUSB* 2>/dev/null || true)

if [[ -z "$devices" ]]; then
  echo "No serial devices found."
  echo ""
  echo "Troubleshooting:"
  echo "  • Check USB connections"
  echo "  • Try: lsusb | grep -i feetech"
  echo "  • Your user needs to be in the 'dialout' group:"
  echo "    sudo usermod -aG dialout \$USER && newgrp dialout"
  exit 1
fi

echo "Connected serial devices:"
echo ""
for dev in $devices; do
  echo -n "  $dev"
  # Try to get device info from udev
  if command -v udevadm &>/dev/null; then
    info=$(udevadm info --name="$dev" 2>/dev/null | grep -E "(ID_VENDOR|ID_MODEL)" | head -2 | tr '\n' ' ' || true)
    echo "  ($info)"
  else
    echo ""
  fi
done

echo ""
echo "Default Laundrobot port mapping:"
echo "  Follower 1: /dev/ttyACM0"
echo "  Follower 2: /dev/ttyACM1"
echo "  Leader:     /dev/ttyACM2"
echo ""
echo "Tip: plug arms in this order — follower1, follower2, leader — for"
echo "consistent /dev/ttyACM numbering. Or install udev rules:"
echo "  sudo ./scripts/setup_udev.sh"
