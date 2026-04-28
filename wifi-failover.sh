#!/bin/bash
# SpotBot WiFi Failover — bascule automatique entre cartes WiFi
# Supporte 2-3 cartes WiFi USB (wlan0, wlan1, wlan2)
# Vérifie la connectivité toutes les 10s et bascule si perte

PING_TARGET="192.168.0.1"  # Passerelle / routeur
PING_TIMEOUT=3
CHECK_INTERVAL=10
SSID="TeALO"
PSK="t3al0l3plusb3au"

LOG=/var/log/spotbot/wifi-failover.log

get_wifi_interfaces() {
    # Liste toutes les interfaces WiFi disponibles
    iw dev 2>/dev/null | awk '$1=="Interface"{print $2}' | sort
}

current_active() {
    # Interface WiFi actuellement connectée
    ip route get $PING_TARGET 2>/dev/null | awk '{for(i=1;i<=NF;i++) if($i=="dev") print $(i+1)}' | head -1
}

is_connected() {
    local iface=$1
    ping -I $iface -c 1 -W $PING_TIMEOUT $PING_TARGET > /dev/null 2>&1
}

connect_wifi() {
    local iface=$1
    echo "$(date) [failover] Connecting $iface to $SSID..." >> $LOG
    # Bring up interface
    ip link set $iface up 2>/dev/null
    # Connect using wpa_supplicant or nmcli
    if command -v nmcli &>/dev/null; then
        nmcli device wifi connect "$SSID" password "$PSK" ifname "$iface" 2>/dev/null
    else
        wpa_cli -i $iface reconfigure 2>/dev/null
    fi
}

echo "$(date) [failover] WiFi failover started" >> $LOG

while true; do
    ACTIVE=$(current_active)
    INTERFACES=$(get_wifi_interfaces)
    
    if [ -n "$ACTIVE" ] && is_connected "$ACTIVE"; then
        # All good
        sleep $CHECK_INTERVAL
        continue
    fi
    
    echo "$(date) [failover] Connection lost on $ACTIVE, trying failover..." >> $LOG
    
    for iface in $INTERFACES; do
        if [ "$iface" != "$ACTIVE" ]; then
            connect_wifi "$iface"
            sleep 3
            if is_connected "$iface"; then
                echo "$(date) [failover] Switched to $iface OK" >> $LOG
                break
            fi
        fi
    done
    
    sleep $CHECK_INTERVAL
done
