#!/usr/bin/env bash
# Configure the Raspberry Pi to broadcast its own offline Wi-Fi hotspot
# (README Milestone 7 — Offline Hotspot).
#
# This must be run ON THE PI (not on a dev machine) since it installs
# system packages and rewrites network interface configuration. It is
# written now so the transfer to hardware is a single script run, but it
# is UNVERIFIED until tested against real Pi hardware.
#
# Usage:
#   sudo scripts/setup_hotspot.sh
set -euo pipefail

if [[ $EUID -ne 0 ]]; then
    echo "This script must be run as root (sudo)." >&2
    exit 1
fi

cd "$(dirname "$0")/.."

HOTSPOT_IFACE="${HOTSPOT_IFACE:-wlan0}"
HOTSPOT_IP="192.168.4.1"

echo "Installing hostapd and dnsmasq..."
apt-get update
apt-get install -y hostapd dnsmasq

echo "Stopping services while we configure them..."
systemctl stop hostapd || true
systemctl stop dnsmasq || true

echo "Assigning static IP ${HOTSPOT_IP} to ${HOTSPOT_IFACE}..."
cat >/etc/network/interfaces.d/photobooth-hotspot <<EOF
allow-hotplug ${HOTSPOT_IFACE}
iface ${HOTSPOT_IFACE} inet static
    address ${HOTSPOT_IP}
    netmask 255.255.255.0
EOF

echo "Installing hostapd.conf..."
install -m 644 config/hotspot/hostapd.conf /etc/hostapd/hostapd.conf
sed -i "s/^interface=.*/interface=${HOTSPOT_IFACE}/" /etc/hostapd/hostapd.conf

# Point the hostapd service at our config file explicitly.
if [[ -f /etc/default/hostapd ]]; then
    sed -i 's|^#\?DAEMON_CONF=.*|DAEMON_CONF="/etc/hostapd/hostapd.conf"|' /etc/default/hostapd
fi

echo "Installing dnsmasq.conf..."
mkdir -p /etc/dnsmasq.d
install -m 644 config/hotspot/dnsmasq.conf /etc/dnsmasq.d/photobooth.conf
sed -i "s/^interface=.*/interface=${HOTSPOT_IFACE}/" /etc/dnsmasq.d/photobooth.conf

echo "Enabling IP forwarding is NOT required (no internet uplink to share)."

echo "Unmasking and enabling hostapd/dnsmasq..."
systemctl unmask hostapd
systemctl enable hostapd
systemctl enable dnsmasq

echo "Starting services..."
systemctl restart dnsmasq
systemctl restart hostapd

echo "Hotspot configured. SSID: PhotoBooth, Pi address: ${HOTSPOT_IP}"
echo "Update config/config.yaml 'sharing.hostname' to ${HOTSPOT_IP} (or photobooth.local) so QR codes resolve for connected guests."
