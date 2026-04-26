#!/usr/bin/env python3
"""
SpotBot — Arduino Auto-Flasher
Utilitaire standalone pour flasher le firmware Arduino depuis le Pi 5.
Usage: python3 arduino_flasher.py <chemin_vers_.hex> [port]
"""

import sys
import glob
import subprocess
import time

try:
    import serial.tools.list_ports
    HAS_SERIAL = True
except ImportError:
    HAS_SERIAL = False


def find_arduino_mega() -> str | None:
    """Trouve automatiquement l'Arduino Mega."""
    if HAS_SERIAL:
        for p in serial.tools.list_ports.comports():
            desc = (p.description or '').lower()
            if 'arduino' in desc or (p.vid == 0x2341 and p.pid in (0x0010, 0x0042)):
                print(f'[FOUND] Arduino Mega: {p.device} ({p.description})')
                return p.device

    for pattern in ['/dev/ttyUSB*', '/dev/ttyACM*']:
        ports = sorted(glob.glob(pattern))
        if ports:
            print(f'[WARN] Auto-detection via glob: essai sur {ports[0]}')
            return ports[0]

    return None


def flash(hex_path: str, port: str) -> bool:
    """Flash le firmware sur l'Arduino Mega."""
    print(f'[FLASH] {hex_path} -> {port}')
    cmd = [
        'avrdude',
        '-p', 'atmega2560',
        '-c', 'wiring',
        '-P', port,
        '-b', '115200',
        '-D',
        '-U', f'flash:w:{hex_path}:i'
    ]
    print(f'[CMD] {" ".join(cmd)}')
    result = subprocess.run(cmd, capture_output=False, timeout=90)
    return result.returncode == 0


def main():
    if len(sys.argv) < 2:
        print('Usage: python3 arduino_flasher.py <firmware.hex> [/dev/ttyUSBx]')
        sys.exit(1)

    hex_file = sys.argv[1]
    port = sys.argv[2] if len(sys.argv) > 2 else find_arduino_mega()

    if port is None:
        print('[ERR] Arduino non trouve. Branchez-le en USB et reessayez.')
        sys.exit(2)

    success = flash(hex_file, port)
    if success:
        print('[OK] Flash reussi! Arduino redemarrage...')
        time.sleep(2)
    else:
        print('[ERR] Echec du flash. Verifiez les connexions.')
        sys.exit(3)


if __name__ == '__main__':
    main()
