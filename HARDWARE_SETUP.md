# SpotBot — Guide de Setup Hardware v2.0

> **Version 2.0** — Ajout capteur ultrason HC-SR04 + module WiFi Alfa USB

## Matériel requis

| Composant | Quantité | Optionnel | Notes |
|-----------|----------|:---------:|-------|
| Raspberry Pi 5 (8 Go min) | 1 | | + carte SD 64 Go min (classe A2) |
| Arduino Mega 2560 | 1 | | Clone compatible OK |
| Servo MG996R | 12 | | Alimentés EN EXTERNE (pas depuis Arduino) |
| MPU6050 (module GY-521) | 1 | | Gyroscope + Accéléromètre I2C |
| **HC-SR04** (capteur ultrason) | 1 | ✅ Optionnel | Détection d'obstacles < 400 cm |
| Caméra USB (mono) | 1 ou 2 | | 1 = mono SLAM, 2 = stéréo SLAM |
| **Module WiFi Alfa USB** | 1 | ✅ Optionnel | AWUS036ACH ou similaire — basculement WiFi |
| Alimentation 6V/10A | 1 | | Pour les servos (non pour le Pi) |
| Alimentation Pi 5V/5A USB-C | 1 | | Officielle Raspberry Pi 5 |
| Câble USB-A vers USB-B | 1 | | Pi 5 → Arduino Mega (flash + Serial) |
| Condensateurs 1000µF 10V | 2 | | Sur alim servos (filtrage pics courant) |

---

## Schéma de câblage

### 1. Servos MG996R → Arduino Mega

> **⚠️ CRITIQUE** : Les 12 servos consomment jusqu'à 30A en pointe. Utilisez une alimentation externe dédiée 5V/10A minimum. Ne jamais alimenter les servos via la broche 5V de l'Arduino.

```
Alimentation Externe 5-6V/10A
  ├─ (+) ──────────────────────────── Fil rouge (VCC) de tous les servos
  └─ (-)  ──── GND commun ─────────── Fil marron/noir de tous les servos
                    │
                    └──────────────── GND Arduino Mega (PIN GND)
```

| Servo | Description    | PIN Arduino | Fil Signal |
|-------|----------------|-------------|-----------|
| 0     | FR Abad        | **D2**      | Jaune/Blanc |
| 1     | FR Upper (cuisse) | **D3**  | Jaune/Blanc |
| 2     | FR Lower (tibia) | **D4**   | Jaune/Blanc |
| 3     | FL Abad        | **D5**      | Jaune/Blanc |
| 4     | FL Upper       | **D6**      | Jaune/Blanc |
| 5     | FL Lower       | **D7**      | Jaune/Blanc |
| 6     | BR Abad        | **D8**      | Jaune/Blanc |
| 7     | BR Upper       | **D9**      | Jaune/Blanc |
| 8     | BR Lower       | **D10**     | Jaune/Blanc |
| 9     | BL Abad        | **D11**     | Jaune/Blanc |
| 10    | BL Upper       | **D12**     | Jaune/Blanc |
| 11    | BL Lower       | **D13**     | Jaune/Blanc |

> Chaque servo : 3 fils — **Marron=GND, Rouge=VCC(alim externe), Jaune/Blanc=Signal(Arduino)**

---

### 2. BNO085 → Arduino Mega *(IMU PRINCIPAL — remplace le MPU6050)*

> **Le BNO085 est fortement recommandé.** Il intègre sa propre fusion gyro+accél+magnétomètre et retourne directement des **quaternions calibrés** — pas besoin de filtre Madgwick côté ROS. Le SLAM rtabmap sera bien plus précis.

| Broche BNO085 | → | Broche Arduino Mega | Notes |
|:---:|:---:|:---:|---|
| VCC | → | **3.3V** | ⚠️ La plupart des breakouts supportent 3.3V et 5V |
| GND | → | **GND** | Masse commune |
| SDA | → | **PIN 20 (SDA)** | Bus I2C partagé avec MPU6050 |
| SCL | → | **PIN 21 (SCL)** | Bus I2C partagé avec MPU6050 |
| INT | → | **D18** | Interruption — améliore la performance (optionnel mais recommandé) |
| RST | → | **D19** | Reset hardware — permet de relancer le BNO085 sans reboot Arduino |
| PS0 | → | **GND** | Sélection protocole I2C (PS0=0, PS1=0 → adresse 0x4A) |
| PS1 | → | **GND** | *(si non connecté, pull-down interne suffit sur la plupart des breakouts)* |

> **Adresse I2C : 0x4A** (PS0=GND, PS1=GND) — pas de conflit avec MPU6050 (0x68)

**Breakouts compatibles :**
| Référence | MCU | Lien |
|-----------|-----|------|
| SparkFun VR IMU Breakout — BNO080/BNO085 | SH-2 | [sparkfun.com](https://www.sparkfun.com/products/22857) |
| Adafruit BNO085 9-DOF IMU | SH-2 | [adafruit.com](https://www.adafruit.com/product/4754) |

**Librairie Arduino requise :**
```
Arduino IDE → Library Manager → "SparkFun BNO08x"
# ou avec arduino-cli:
arduino-cli lib install "SparkFun BNO08x"
```

---

### 3. Raspberry Pi 5 → Arduino Mega

```
Raspberry Pi 5                     Arduino Mega
  USB-A port    ═══════════════════  USB-B port
                (câble USB standard)

Communication : Serial @ 115200 baud
Utilisation  : Flash firmware + communication JSON bidirectionnelle
```

> L'Arduino se connecte automatiquement comme `/dev/ttyUSB0` ou `/dev/ttyACM0` sur le Pi 5.

---

### 4. Caméra(s) USB → Raspberry Pi 5

**Mode Monoculaire :**
```
Pi 5 USB port ──── Caméra USB unique
                   Apparait comme /dev/video0
```

**Mode Stéréo (2 cameras) :**
```
Pi 5 USB port 1 ──── Caméra GAUCHE → /dev/video0
Pi 5 USB port 2 ──── Caméra DROITE → /dev/video1
```
> Placer les deux caméras parallèles, séparées d'environ 6-12 cm (baseline stéréo).

---

### 5. HC-SR04 (capteur ultrason) → Arduino Mega *(OPTIONNEL)*

> Le HC-SR04 permet au robot de détecter les obstacles devant lui en temps réel.
> Le Pi 5 reçoit les données via le bridge JSON et publie sur `/sensors/ultrasonic`.

| Broche HC-SR04 | → | Broche Arduino Mega | Fil couleur courant |
|:--------------:|:---:|:-------------------:|:-------------------:|
| VCC | → | **5V** Arduino | Rouge |
| GND | → | **GND** commun | Noir/Marron |
| TRIG | → | **D22** | Jaune/Orange |
| ECHO | → | **D23** | Bleu/Vert |

> **Note :** Ne pas utiliser D2–D13 (réservés aux servos). D22 et D23 sont des GPIO libres du Mega.

**Placement recommandé sur le robot :**
```
      ┌────────┐
      │ HC-SR04│  ← Fixé à l'avant du chassis, centré, à ~5 cm du sol
      │ [o] [o]│     Angle d'émission ~15° — portée 2 cm à 400 cm
      └────────┘
          │
         ↓ détecte les obstacles dans un cône de ~15°
```

**Topic ROS 2 publié :**
```bash
ros2 topic echo /sensors/ultrasonic  # sensor_msgs/Range (distance en mètres)
ros2 topic echo /sensors/obstacle    # std_msgs/Bool (True si < 30 cm)
```

---

### 6. Module WiFi Alfa USB → Raspberry Pi 5 *(OPTIONNEL)*

> Le module Alfa fournit une **deuxième interface WiFi** pour le Pi 5.
> Le WiFi watchdog surveille les signaux et bascule automatiquement vers la meilleure connexion.
> **Aucune configuration manuelle nécessaire** — l'auto-détection se fait par VID/PID USB.

| Connexion | Description |
|-----------|-------------|
| Alfa USB → **Port USB Pi 5** | Plug & Play — détecté automatiquement |
| Antenne Alfa | Visser sur le connecteur SMA du module |

**Modules compatibles (testés) :**
| Modèle | Chipset | VID:PID USB |
|--------|---------|-------------|
| AWUS036ACH | RTL8812AU | 0bda:8812 |
| AWUS036AC | RTL8812AU | 0bda:8812 |
| AWUS036NH | RT3070 | 148f:3070 |
| AWUS036H | RT3070 | 148f:5370 |

**Comportement automatique :**
```
Signal wlan0 > -70 dBm  →  Streaming via wlan0 (Pi intégré)
Signal wlan0 < -70 dBm  →  Basculement vers Alfa (wlan1) sans coupure
Alfa non branché        →  Mono-WiFi standard (fonctionnement normal)
```

**Topics ROS 2 :**
```bash
ros2 topic echo /wifi/status      # std_msgs/String
ros2 topic echo /wifi/alfa_active # std_msgs/Bool  (True = Alfa utilisé)
```

---

```
┌─────────────────────────────────────────────────────────┐
│                    RASPBERRY PI 5                        │
│                                                          │
│  USB-C ◄── Alim 5V/5A officielle                        │
│                                                          │
│  USB-A ──► Arduino Mega (Serial + Flash)                 │
│  USB-A ──► Caméra gauche /dev/video0                     │
│  USB-A ──► Caméra droite /dev/video1 (stéréo optionnel) │
│                                                          │
│  GPIO  ──► (libre pour extensions futures)               │
└─────────────────────────────────────────────────────────┘
                         │ USB
                         ▼
┌─────────────────────────────────────────────────────────┐
│                   ARDUINO MEGA 2560                      │
│                                                          │
│  D2 ──► Servo 0  (FR Abad)    │ I2C SDA (20) ◄── MPU6050│
│  D3 ──► Servo 1  (FR Upper)   │ I2C SCL (21) ◄── MPU6050│
│  D4 ──► Servo 2  (FR Lower)   │                          │
│  D5 ──► Servo 3  (FL Abad)    │                          │
│  D6 ──► Servo 4  (FL Upper)   │                          │
│  D7 ──► Servo 5  (FL Lower)   │                          │
│  D8 ──► Servo 6  (BR Abad)    │                          │
│  D9 ──► Servo 7  (BR Upper)   │                          │
│  D10──► Servo 8  (BR Lower)   │                          │
│  D11──► Servo 9  (BL Abad)    │                          │
│  D12──► Servo 10 (BL Upper)   │                          │
│  D13──► Servo 11 (BL Lower)   │                          │
│                                                          │
│  GND ◄────────────── GND commun servos + MPU6050         │
└─────────────────────────────────────────────────────────┘
                         │
          ┌──────────────┘
          │ VCC Signal uniquement
          ▼
┌─────────────────────────────────────────────────────────┐
│             ALIMENTATION EXTERNE 5-6V / 10A              │
│                                                          │
│  (+) ──────────────────────────────── VCC (rouge) servos │
│  (-) ──── GND commun Arduino ──────── GND (marron) servos│
│                                                          │
│  ⚠️ Condensateurs 100µF (1000µF recommandé) sur les      │
│     bornes + et - pour filtrer les pics de courant       │
└─────────────────────────────────────────────────────────┘
```

---

## Checklist avant mise sous tension

**Obligatoire :**
- [ ] GND Arduino connecté au GND de l'alimentation externe servos
- [ ] VCC servos branché sur **alimentation externe 6V** (JAMAIS Arduino 5V)
- [ ] Condensateurs 1000µF sur bornes alim servos (anti-pics courant)
- [ ] Tous les fils signal servos sur les bonnes pins (D2 à D13)
- [ ] MPU6050 : SDA→PIN20, SCL→PIN21, VCC→3.3V, GND→GND
- [ ] Câble USB Pi5↔Arduino branché
- [ ] Alimentation Pi 5 branchée séparément (USB-C 5V/5A)

**HC-SR04 (si installé) :**
- [ ] TRIG → **D22**, ECHO → **D23**
- [ ] VCC → **5V Arduino** (pas l'alim externe)
- [ ] GND → GND commun
- [ ] Capteur fixé à l'avant du chassis, centré, dégagé

**Module Alfa (si installé) :**
- [ ] Branché sur port USB Pi 5
- [ ] Antenne vissée sur connecteur SMA
- [ ] Drivers installés (`bash install/setup_wifi.sh`)

---

## Installation logicielle séquentielle

```bash
# Sur le Raspberry Pi 5 (Ubuntu 24.04 AArch64)

# 1. Cloner le repo
git clone https://github.com/TON_USERNAME/spotbot-ros2.git
cd spotbot-ros2

# 2. Installer ROS 2 Jazzy
bash install/install_ros2.sh

# 3. Installer les dépendances
bash install/install_deps.sh

# 4. Builder le workspace
bash install/build_workspace.sh

# 5. Lancer (tout-en-un)
source ~/spotbot-ros2/ros2_ws/install/setup.bash
ros2 launch spotbot_bringup spotbot.launch.py mode:=mono
```

---

## Calibration des servos

Après installation, ajustez les valeurs dans `spotbot_controller.ino` :

```cpp
// Ajustez ces valeurs selon votre montage réel (0-180 deg)
const float SERVO_STAND[NUM_SERVOS] = {
    90, 90, 90,  // FR: abad, upper, lower
    90, 90, 90,  // FL: ...
    90, 90, 90,  // BR: ...
    90, 90, 90   // BL: ...
};
```

Commande de test servo individuel depuis le Pi :
```bash
ros2 topic pub /cmd_joint_angles std_msgs/Float32MultiArray \
  "data: [90.0, 90.0, 90.0, 90.0, 90.0, 90.0, 90.0, 90.0, 90.0, 90.0, 90.0, 90.0]"
```

---

## Flash du firmware Arduino depuis le Pi 5

```bash
# Compiler avec Arduino CLI (recommandé sur le Pi)
arduino-cli compile -b arduino:avr:mega arduino/spotbot_controller/

# Ou utiliser l'IDE Arduino sur un PC puis copier le .hex sur le Pi

# Flash automatique (le node ROS le fait au démarrage si configuré)
python3 ros2_ws/src/spotbot_arduino_bridge/spotbot_arduino_bridge/arduino_flasher.py \
    arduino/spotbot_controller/spotbot_controller.ino.hex

# Flash manuel
avrdude -p atmega2560 -c wiring -P /dev/ttyUSB0 -b 115200 \
    -U flash:w:spotbot_controller.hex:i
```
