#!/usr/bin/env python3
"""
SpotBot — WiFi Manager
======================
Gestion du module Alfa USB WiFi optionnel.

Fonctionnalités:
  - Auto-détection du module Alfa (par VID/PID USB ou nom d'interface)
  - Retourne l'interface réseau disponible la plus adaptée au streaming
  - Utilisé par camera_stream_node et wifi_watchdog_node

VID/PID Alfa courants:
  148f:3070  — Alfa AWUS036H / AWUS036NH (Ralink RT3070)
  148f:5370  — Alfa AWUS036H v2 (Ralink RT5370)
  0bda:8812  — Alfa AWUS036AC (Realtek RTL8812AU)
  0bda:881a  — Alfa AWUS036ACH (Realtek RTL8812BU)
  0bda:b812  — Alfa Network divers (RTL8812BU)
"""

import subprocess
import re
import os
import socket
import time


# VID/PID USB connus pour les cartes Alfa
ALFA_VENDOR_IDS = {'148f', '0bda'}
ALFA_PRODUCT_IDS = {'3070', '5370', '8812', '881a', 'b812', '8811', '88b2'}


def detect_alfa_interface() -> str | None:
    """
    Détecte si un module Alfa est branché et retourne son interface réseau.

    Returns:
        str: nom de l'interface (ex: 'wlan1') ou None si absent
    """
    # ---- Méthode 1 : lsusb ----
    try:
        result = subprocess.run(['lsusb'], capture_output=True, text=True, timeout=5)
        for line in result.stdout.splitlines():
            m = re.search(r'ID\s+([0-9a-f]{4}):([0-9a-f]{4})', line, re.IGNORECASE)
            if m:
                vid, pid = m.group(1).lower(), m.group(2).lower()
                if vid in ALFA_VENDOR_IDS and pid in ALFA_PRODUCT_IDS:
                    # Trouver l'interface correspondante
                    iface = _find_wifi_interface_for_usb(vid, pid)
                    if iface:
                        return iface
    except (subprocess.TimeoutExpired, FileNotFoundError):
        pass

    # ---- Méthode 2 : chercher wlan1+ (interface supplémentaire) ----
    interfaces = _list_wifi_interfaces()
    builtin = _get_builtin_wifi_interface()
    extras = [i for i in interfaces if i != builtin]
    if extras:
        # Vérifier que l'interface est UP
        for iface in extras:
            if _is_interface_up(iface):
                return iface
        return extras[0]  # Retourner même si down (sera activé)

    return None


def _find_wifi_interface_for_usb(vid: str, pid: str) -> str | None:
    """Trouve l'interface réseau associée à un VID/PID USB."""
    try:
        # Chercher dans /sys/bus/usb/drivers/
        result = subprocess.run(
            ['find', '/sys/bus/usb/devices', '-name', 'idVendor', '-exec', 'grep', '-l', vid, '{}', ';'],
            capture_output=True, text=True, timeout=5
        )
        # Chercher les interfaces réseau dans /sys/class/net
        wifi_ifaces = _list_wifi_interfaces()
        if len(wifi_ifaces) > 1:
            # L'interface Alfa est probablement la deuxième
            builtin = _get_builtin_wifi_interface()
            for iface in wifi_ifaces:
                if iface != builtin:
                    return iface
    except (subprocess.TimeoutExpired, FileNotFoundError):
        pass
    return None


def _list_wifi_interfaces() -> list[str]:
    """Liste toutes les interfaces WiFi disponibles."""
    interfaces = []
    try:
        net_dir = '/sys/class/net'
        for iface in os.listdir(net_dir):
            wireless_path = os.path.join(net_dir, iface, 'wireless')
            if os.path.exists(wireless_path):
                interfaces.append(iface)
    except OSError:
        pass
    return sorted(interfaces)


def _get_builtin_wifi_interface() -> str:
    """Retourne l'interface WiFi intégrée (généralement wlan0)."""
    # L'interface intégrée du Pi 5 est presque toujours wlan0
    if os.path.exists('/sys/class/net/wlan0'):
        return 'wlan0'
    ifaces = _list_wifi_interfaces()
    return ifaces[0] if ifaces else 'wlan0'


def _is_interface_up(iface: str) -> bool:
    """Vérifie si une interface réseau est active."""
    try:
        with open(f'/sys/class/net/{iface}/operstate') as f:
            return f.read().strip() == 'up'
    except OSError:
        return False


def get_best_interface_ip(prefer_alfa: bool = False) -> tuple[str, str]:
    """
    Retourne (interface, ip) du meilleur chemin réseau disponible.

    Args:
        prefer_alfa: Si True, préfère le module Alfa si disponible

    Returns:
        (interface_name, ip_address)
    """
    alfa = detect_alfa_interface()
    builtin = _get_builtin_wifi_interface()

    if prefer_alfa and alfa:
        ip = _get_interface_ip(alfa)
        if ip:
            return alfa, ip

    # Utiliser l'interface principale
    ip = _get_interface_ip(builtin)
    if ip:
        return builtin, ip

    # Fallback: toute interface UP avec une IP
    for iface in _list_wifi_interfaces():
        ip = _get_interface_ip(iface)
        if ip:
            return iface, ip

    return 'wlan0', '0.0.0.0'


def _get_interface_ip(iface: str) -> str | None:
    """Retourne l'IP d'une interface réseau."""
    try:
        result = subprocess.run(
            ['ip', '-4', 'addr', 'show', iface],
            capture_output=True, text=True, timeout=3
        )
        m = re.search(r'inet\s+([\d.]+)', result.stdout)
        if m:
            return m.group(1)
    except (subprocess.TimeoutExpired, FileNotFoundError):
        pass
    return None


def get_interface_signal_dbm(iface: str) -> int | None:
    """Retourne la puissance du signal WiFi en dBm (-100 = très mauvais, 0 = parfait)."""
    try:
        result = subprocess.run(
            ['iwconfig', iface], capture_output=True, text=True, timeout=3
        )
        m = re.search(r'Signal level=(-?\d+)\s*dBm', result.stdout)
        if m:
            return int(m.group(1))
    except (subprocess.TimeoutExpired, FileNotFoundError):
        pass
    return None


def print_network_status():
    """Affiche l'état réseau complet (debug)."""
    builtin = _get_builtin_wifi_interface()
    alfa = detect_alfa_interface()

    print(f"Interface principale: {builtin} | IP: {_get_interface_ip(builtin)} | "
          f"Signal: {get_interface_signal_dbm(builtin)} dBm")
    if alfa:
        print(f"Module Alfa détecté: {alfa} | IP: {_get_interface_ip(alfa)} | "
              f"Signal: {get_interface_signal_dbm(alfa)} dBm")
    else:
        print("Module Alfa: non détecté (optionnel)")


if __name__ == '__main__':
    print_network_status()
