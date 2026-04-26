#!/bin/bash
# ============================================================
# SpotBot — SETUP COMPLET EN UNE SEULE COMMANDE
# Usage: bash setup.sh
# Supporte Ubuntu 24.04 (Noble) et Debian 13 (Trixie)
# ============================================================
set -e

GREEN='\033[0;32m'; YELLOW='\033[1;33m'; RED='\033[0;31m'
CYAN='\033[0;36m'; BOLD='\033[1m'; NC='\033[0m'


echo -e "${CYAN}${BOLD}"
cat << 'BANNER'
  ╔═══════════════════════════════════════════════════╗
  ║        🐾  S P O T B O T  —  S E T U P  🐾       ║
  ║      ROS 2 Jazzy · V-SLAM · Arduino Mega          ║
  ╚═══════════════════════════════════════════════════╝
BANNER
echo -e "${NC}"

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
info()    { echo -e "${GREEN}  ✔ ${NC}$1"; }
warning() { echo -e "${YELLOW}  ⚠ ${NC}$1"; }
step()    { echo -e "\n${CYAN}${BOLD}▶ $1${NC}"; }

# ---- Verification OS ----
step "Verification du systeme"
. /etc/os-release
info "OS: $PRETTY_NAME ($(uname -m))"

if [[ "$(uname -m)" != "aarch64" ]]; then
    warning "Architecture non ARM64 detectee. Ce script est optimise pour Raspberry Pi 5."
    warning "Continuer sur cette machine? (Ctrl+C pour annuler)"
    sleep 3
fi

# Detect OS: ubuntu/debian
if [[ "$ID" == "ubuntu" && "$VERSION_CODENAME" == "noble" ]]; then
    ROS_INSTALL_MODE="apt"
    ROS_SETUP="/opt/ros/jazzy/setup.bash"
elif [[ "$ID" == "debian" ]]; then
    ROS_INSTALL_MODE="source"
    ROS_SETUP="/opt/ros2_jazzy/install/setup.bash"
else
    warning "OS non reconnu ($ID $VERSION_CODENAME). Tentative en mode source..."
    ROS_INSTALL_MODE="source"
    ROS_SETUP="/opt/ros2_jazzy/install/setup.bash"
fi

info "Mode d'installation ROS 2: $ROS_INSTALL_MODE"

# ---- Etape 1: ROS 2 ----
step "Etape 1/4 — Installation ROS 2 Jazzy (mode: $ROS_INSTALL_MODE)"
if [[ "$ROS_INSTALL_MODE" == "apt" ]]; then
    bash "$SCRIPT_DIR/install/install_ros2.sh"
else
    bash "$SCRIPT_DIR/install/install_ros2_from_source.sh"
fi

# ---- Etape 2: Dependances ----
step "Etape 2/4 — Installation des dependances"
source "$ROS_SETUP"
ROS_SETUP="$ROS_SETUP" bash "$SCRIPT_DIR/install/install_deps.sh"

# ---- Etape 3: Build workspace ----
step "Etape 3/4 — Build du workspace ROS 2"
source "$ROS_SETUP"
ROS_SETUP="$ROS_SETUP" bash "$SCRIPT_DIR/install/build_workspace.sh"

# ---- Etape 4: Arduino ----
step "Etape 4/4 — Configuration Arduino"
if ls /dev/ttyUSB* /dev/ttyACM* 2>/dev/null | grep -q .; then
    info "Arduino detecte! Flash du firmware..."
    bash "$SCRIPT_DIR/install/install_arduino.sh"
else
    warning "Arduino non detecte. Branchez-le en USB et relancez:"
    warning "  bash install/install_arduino.sh"
fi

# ---- Fin ----
echo ""
echo -e "${GREEN}${BOLD}"
cat << 'DONE'
  ╔═══════════════════════════════════════════════════╗
  ║           ✅  SETUP TERMINE AVEC SUCCES!           ║
  ║                                                   ║
  ║  Lancez le robot avec:                            ║
  ║    ros2 launch spotbot_bringup spotbot.launch.py  ║
  ║                                                   ║
  ║  Options:                                         ║
  ║    mode:=mono    (1 camera USB)                   ║
  ║    mode:=stereo  (2 cameras USB)                  ║
  ║    rviz:=true    (visualisation 3D)               ║
  ╚═══════════════════════════════════════════════════╝
DONE
echo -e "${NC}"
