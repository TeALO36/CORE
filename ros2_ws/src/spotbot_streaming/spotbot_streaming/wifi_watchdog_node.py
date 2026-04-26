#!/usr/bin/env python3
"""
SpotBot — WiFi Watchdog Node
=============================
Basculement WiFi automatique sans coupure de connexion.

Stratégie :
  - Surveille le signal des interfaces WiFi disponibles (Pi5 intégré + Alfa)
  - Si le signal de l'interface principale baisse sous le seuil → bascule vers Alfa
  - Si Alfa pas disponible → utilise seulement l'interface principale
  - Utilise le "metric" des routes Linux pour un basculement transparent
  - Aucune coupure : les deux interfaces restent UP en permanence, seule la route
    préférée change (metric 100 = prioritaire, metric 200 = backup)

Requis: nmcli (NetworkManager) ou iproute2
"""

import subprocess
import time
import os
import re

import rclpy
from rclpy.node import Node
from std_msgs.msg import String, Bool

from .wifi_manager import (
    detect_alfa_interface,
    _get_builtin_wifi_interface,
    _get_interface_ip,
    _is_interface_up,
    get_interface_signal_dbm,
)


class WifiWatchdogNode(Node):
    """
    Surveille les interfaces WiFi et bascule le routing pour maintenir
    la meilleure connexion en permanence.
    """

    CHECK_INTERVAL    = 5.0    # Vérification toutes les 5 secondes
    SIGNAL_THRESHOLD  = -70    # dBm : sous ce seuil, on bascule vers Alfa
    SIGNAL_HYSTERESIS = 5      # dBm : marge pour éviter le ping-pong
    METRIC_PRIMARY    = 100    # Metric route principale (plus petit = prioritaire)
    METRIC_BACKUP     = 200    # Metric route backup

    def __init__(self):
        super().__init__('wifi_watchdog')

        self.declare_parameter('signal_threshold',  self.SIGNAL_THRESHOLD)
        self.declare_parameter('check_interval',    self.CHECK_INTERVAL)
        self.declare_parameter('enabled',           True)

        self._threshold      = self.get_parameter('signal_threshold').value
        self._interval       = self.get_parameter('check_interval').value
        self._enabled        = self.get_parameter('enabled').value

        # ---- Publishers ----
        self._status_pub = self.create_publisher(String, '/wifi/status',    10)
        self._alfa_pub   = self.create_publisher(Bool,   '/wifi/alfa_active', 10)

        # ---- État interne ----
        self._builtin   = _get_builtin_wifi_interface()
        self._alfa      = detect_alfa_interface()
        self._using_alfa = False
        self._last_switch_time = 0.0

        if self._alfa:
            self.get_logger().info(
                f'WiFi Watchdog actif | Interface principale: {self._builtin} | '
                f'Alfa: {self._alfa} | Seuil bascule: {self._threshold} dBm'
            )
            self._ensure_both_interfaces_up()
        else:
            self.get_logger().info(
                f'WiFi Watchdog: Alfa non détecté. Monitoring seul sur {self._builtin}.'
            )

        self._timer = self.create_timer(self._interval, self._check)

    # ------------------------------------------------------------------
    # Boucle principale
    # ------------------------------------------------------------------

    def _check(self):
        """Vérifie les signaux et bascule si nécessaire."""
        if not self._enabled:
            return

        builtin_dbm = get_interface_signal_dbm(self._builtin)
        alfa_dbm    = get_interface_signal_dbm(self._alfa) if self._alfa else None

        status_parts = [f'{self._builtin}:{builtin_dbm}dBm']
        if alfa_dbm is not None:
            status_parts.append(f'{self._alfa}:{alfa_dbm}dBm')

        self.get_logger().debug(' | '.join(status_parts))
        self._publish_status(' | '.join(status_parts))

        if not self._alfa:
            return  # Pas de basculement possible

        # Logique de basculement
        now = time.time()
        cooldown = 10.0  # Minimum 10s entre deux bascules

        if now - self._last_switch_time < cooldown:
            return

        if builtin_dbm is not None and builtin_dbm < self._threshold:
            # Signal principal faible → préférer Alfa
            if not self._using_alfa and alfa_dbm and alfa_dbm > (builtin_dbm + self.SIGNAL_HYSTERESIS):
                self.get_logger().warn(
                    f'Signal {self._builtin} faible ({builtin_dbm} dBm). '
                    f'Bascule vers Alfa ({self._alfa}: {alfa_dbm} dBm)'
                )
                self._prefer_interface(self._alfa, self._builtin)
                self._using_alfa = True
                self._last_switch_time = now

        elif builtin_dbm is not None and builtin_dbm > (self._threshold + self.SIGNAL_HYSTERESIS):
            # Signal principal bon → revenir à l'interface principale
            if self._using_alfa:
                self.get_logger().info(
                    f'Signal {self._builtin} restauré ({builtin_dbm} dBm). '
                    f'Retour à l\'interface principale.'
                )
                self._prefer_interface(self._builtin, self._alfa)
                self._using_alfa = False
                self._last_switch_time = now

        # Publier l'état Alfa
        msg = Bool()
        msg.data = self._using_alfa
        self._alfa_pub.publish(msg)

    # ------------------------------------------------------------------
    # Gestion des routes Linux
    # ------------------------------------------------------------------

    def _ensure_both_interfaces_up(self):
        """S'assure que les deux interfaces sont actives avec les bons metrics."""
        self.get_logger().info('Configuration du routing dual-WiFi...')

        # S'assurer que l'interface Alfa est gérée par NetworkManager
        try:
            subprocess.run(
                ['nmcli', 'device', 'set', self._alfa, 'managed', 'yes'],
                capture_output=True, timeout=5
            )
        except (subprocess.TimeoutExpired, FileNotFoundError):
            pass

        # Appliquer les metrics initiaux (principale prioritaire)
        self._set_metric(self._builtin, self.METRIC_PRIMARY)
        self._set_metric(self._alfa,    self.METRIC_BACKUP)
        self.get_logger().info(
            f'Routing: {self._builtin} metric={self.METRIC_PRIMARY} (prioritaire) | '
            f'{self._alfa} metric={self.METRIC_BACKUP} (backup)'
        )

    def _prefer_interface(self, preferred: str, secondary: str):
        """
        Bascule la route préférée sans coupure :
        - Change uniquement les metrics des routes existantes
        - Les deux interfaces restent connectées (pas de déconnexion)
        """
        # Méthode douce : modifier la metric via NetworkManager
        # NetworkManager gère le changement de route de façon transparente
        try:
            # Baisser metric de l'interface préférée
            subprocess.run([
                'nmcli', 'connection', 'modify',
                self._get_connection_name(preferred),
                'ipv4.route-metric', str(self.METRIC_PRIMARY)
            ], capture_output=True, timeout=5)

            # Augmenter metric de l'interface secondaire
            subprocess.run([
                'nmcli', 'connection', 'modify',
                self._get_connection_name(secondary),
                'ipv4.route-metric', str(self.METRIC_BACKUP)
            ], capture_output=True, timeout=5)

            # Réappliquer la connexion (sans déconnecter)
            subprocess.run([
                'nmcli', 'device', 'reapply', preferred
            ], capture_output=True, timeout=5)

        except (subprocess.TimeoutExpired, FileNotFoundError):
            # Fallback: modifier la route directement avec 'ip route'
            self._ip_route_prefer(preferred, secondary)

    def _ip_route_prefer(self, preferred: str, secondary: str):
        """Fallback: modifier les routes via iproute2 directement."""
        try:
            # Obtenir la gateway de l'interface préférée
            gw = self._get_gateway(preferred)
            if gw:
                subprocess.run([
                    'ip', 'route', 'change', 'default',
                    'via', gw, 'dev', preferred,
                    'metric', str(self.METRIC_PRIMARY)
                ], capture_output=True, timeout=5)
        except (subprocess.TimeoutExpired, FileNotFoundError) as e:
            self.get_logger().error(f'Erreur ip route: {e}')

    def _set_metric(self, iface: str, metric: int):
        """Applique un metric de route pour une interface."""
        gw = self._get_gateway(iface)
        if gw:
            try:
                subprocess.run(
                    ['ip', 'route', 'change', 'default', 'via', gw,
                     'dev', iface, 'metric', str(metric)],
                    capture_output=True, timeout=5
                )
            except (subprocess.TimeoutExpired, FileNotFoundError):
                pass

    def _get_gateway(self, iface: str) -> str | None:
        """Retourne la passerelle par défaut d'une interface."""
        try:
            result = subprocess.run(
                ['ip', 'route', 'show', 'dev', iface],
                capture_output=True, text=True, timeout=3
            )
            m = re.search(r'default via ([\d.]+)', result.stdout)
            if m:
                return m.group(1)
        except (subprocess.TimeoutExpired, FileNotFoundError):
            pass
        return None

    def _get_connection_name(self, iface: str) -> str:
        """Retourne le nom de connexion NetworkManager pour une interface."""
        try:
            result = subprocess.run(
                ['nmcli', '-t', '-f', 'NAME,DEVICE', 'connection', 'show', '--active'],
                capture_output=True, text=True, timeout=5
            )
            for line in result.stdout.splitlines():
                if f':{iface}' in line:
                    return line.split(':')[0]
        except (subprocess.TimeoutExpired, FileNotFoundError):
            pass
        return iface  # Fallback: même nom

    def _publish_status(self, status: str):
        msg = String()
        mode = 'alfa' if self._using_alfa else 'builtin'
        msg.data = f'mode={mode} | {status}'
        self._status_pub.publish(msg)


def main(args=None):
    rclpy.init(args=args)
    node = WifiWatchdogNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
