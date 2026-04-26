# 🐕 SpotBot-ROS2

SpotBot est un robot quadrupède (refork) basé sur un **Raspberry Pi 5** et un **Arduino Mega 2560**, propulsé par **ROS 2 Jazzy Jalisco** sur Debian 13 (Trixie).

## 🚀 Caractéristiques
- **Cerveau** : Raspberry Pi 5 (8GB RAM)
- **Contrôleur Moteurs** : Arduino Mega 2560 R3
- **Système** : Debian 13 (Trixie) avec ROS 2 Jazzy compilé depuis les sources.
- **Vision** : V-SLAM via RTAB-Map et caméra USB.
- **Interface** : Dashboard Web via ROSBoard.

## 🛠️ Installation Rapide
Le projet utilise une installation personnalisée de ROS 2 pour supporter Debian 13.
```bash
# Sourcing de l'environnement
source /opt/ros2_jazzy/install/setup.bash
source ~/spotbot-ros2/ros2_ws/install/setup.bash
```

## 🎮 Gestion du Robot
Une commande unifiée a été créée pour simplifier l'usage quotidien :
- `spotbot start`   : Lance les nodes moteurs, caméra et interface web.
- `spotbot stop`    : Arrête tous les processus ROS 2.
- `spotbot status`  : Affiche la température, RAM et les nodes actifs.
- `spotbot logs`    : Visualise le flux de données en temps réel.

## 📺 Interface de Debug
Accédez au dashboard en direct depuis n'importe quel appareil sur le même réseau :
👉 **http://192.168.0.51:8888**

## 📂 Structure du Workspace
- `spotbot_arduino_bridge` : Pont USB Serial entre Pi 5 et Arduino.
- `spotbot_motion`         : Algorithmes de cinématique et mouvements.
- `spotbot_streaming`      : Gestion du flux vidéo et WiFi.
- `spotbot_description`    : Modèle 3D (URDF) du robot.
- `spotbot_bringup`        : Launchers principaux du système.

---
Projet développé avec ❤️ pour la robotique quadrupède.
