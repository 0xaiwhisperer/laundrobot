#!/usr/bin/env bash
# setup_udev.sh — install persistent udev symlinks for Laundrobot devices
# Run as root: sudo ./scripts/setup_udev.sh
set -euo pipefail

if [[ $EUID -ne 0 ]]; then
  echo "Please run as root: sudo $0"
  exit 1
fi

RULES_FILE="/etc/udev/rules.d/99-laundrobot.rules"

echo "Installing Laundrobot udev rules → $RULES_FILE"

cat > "$RULES_FILE" << 'RULES'
# Laundrobot — persistent device names for SO-101 / SO-100 arms
# These rules create stable symlinks regardless of plug-in order.
#
# To find the ATTRS{serial} value for your device:
#   udevadm info --name=/dev/ttyACM0 --attribute-walk | grep serial
#
# Replace the serial numbers below with your actual device serials.

# Follower 1 (primary robot arm)
# SUBSYSTEM=="tty", ATTRS{idVendor}=="0483", ATTRS{serial}=="YOUR_SERIAL_1", SYMLINK+="laundrobot-follower1"

# Follower 2 (second robot arm — dual-arm setups)
# SUBSYSTEM=="tty", ATTRS{idVendor}=="0483", ATTRS{serial}=="YOUR_SERIAL_2", SYMLINK+="laundrobot-follower2"

# Leader (operator arm)
# SUBSYSTEM=="tty", ATTRS{idVendor}=="0483", ATTRS{serial}=="YOUR_SERIAL_3", SYMLINK+="laundrobot-leader1"
RULES

echo ""
echo "Rules file written. Next steps:"
echo ""
echo "1. Find the serial number of each arm:"
echo "     udevadm info --name=/dev/ttyACM0 --attribute-walk | grep serial"
echo ""
echo "2. Edit $RULES_FILE and uncomment/fill in the serial numbers"
echo ""
echo "3. Reload udev rules:"
echo "     udevadm control --reload-rules && udevadm trigger"
echo ""
echo "4. Replug the arms — they should now appear as:"
echo "     /dev/laundrobot-follower1"
echo "     /dev/laundrobot-follower2"
echo "     /dev/laundrobot-leader1"
echo ""
echo "5. Update Laundrobot to use these stable paths:"
echo "     laundrobot --follower /dev/laundrobot-follower1 \\"
echo "                --leader  /dev/laundrobot-leader1"

# Add current user to dialout group if not already a member
CURRENT_USER=${SUDO_USER:-$USER}
if ! groups "$CURRENT_USER" | grep -q dialout; then
  echo ""
  echo "Adding $CURRENT_USER to the dialout group (required for serial access)..."
  usermod -aG dialout "$CURRENT_USER"
  echo "Done — log out and back in for this to take effect."
fi
