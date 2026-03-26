<div align="center">
  <h1>🤖 Bastet AI V2 - CORE & Simulation</h1>
  <p><i>Le système nerveux central et distribué du robot quadrupède Bastet.</i></p>
</div>

---

## 📖 Présentation du Projet
**Bastet CORE** est une architecture d'intelligence artificielle distribuée conçue pour contrôler un robot physique de type SpotMicro. Il permet de déporter les calculs lourds (Modèles de Langage, Vision par Ordinateur) sur des machines puissantes tout en pilotant le robot à distance (via réseau local ou relais 4G).

Récemment, le projet a fusionné avec **SpotMicroAI** pour y inclure un environnement de simulation PyBullet, permettant à l'IA de s'entraîner et d'interagir virtuellement via réseau UDP avant le déploiement final sur le matériel matériel physique.

## 🎯 Fonctionnalités Clés
- **IA Déportée (NVIDIA NIM)** : Le système utilise l'API cloud NVIDIA pour la prise de décision, avec des modèles ultra-rapides (Llama 3 Instruct), économisant ainsi la batterie et le calcul du robot.
- **Vision & Voix Locales** : La reconnaissance faciale (YOLO) et les flux de parole audios (STT/TTS) tournent localement sur les PC du réseau.
- **Routage Automatique** : Le serveur *Hub* découvre et associe automatiquement les nœuds de la grille via UDP Broadcast ou Websockets.
- **Interface Web temps-réel** : Un dashboard complet en React permet de configurer l'IA, voir le flux caméra et l'historique de discussion localement depuis le navigateur.
- **Simulation 3D intégrée** : Le dossier `simulation/` inclut le framework SpotMicroAI et PyBullet pour visualiser et tester la marche du quadrupède en direct !

---

## ⚙️ Composants du Système

L'architecture est hautement modulaire et repose sur différents **Nœuds (Nodes)** :

1. **HUB (Port 8000)** : Le chef d'orchestre. Un serveur FastAPI avec WebSocket qui lie tous les nœuds et qui sert l'interface Web HTML/JS à l'utilisateur.
2. **VISION** : Gère la webcam du robot, analyse l'image, reconnait les visages pré-enregistrés.
3. **LLM (AI Agent)** : Connecté à NVIDIA NIM. Il ingère le contexte visuel ("Paul est devant toi"), l'agenda connecté de la cible (via intégration MyGES), et la requête vocale de l'utilisateur pour générer une réponse texte/voix, ainsi que des marqueurs de commandes physiques (Ex: `[CMD: avancer]`).
4. **SIMULATION / ROBOT** : Reçoit silencieusement les ordres physiques (`AVANCER`, `STOP`) via un socket local en **UDP (Port 5005)** et résout les angles des moteurs (*PyBullet / Inverse Kinematics*).

---

## 🚀 Installation & Lancement

### 1. Prérequis
- Python 3.10+
- Node.js (pour compiler l'interface web si besoin)
- Une clé API NVIDIA NIM (à placer dans `config.json` à la racine)

```bash
git clone <URL_DU_REPO>
cd Bastet_CORE
pip install -r requirements.txt
```

### 2. Lancement en 1 Clic (Recommandé)
Sous Windows, un script global est prêt pour vous :
Double-cliquez sur le fichier **`run_all.bat`**.

Ce script va automatiquement :
- Vérifier et compiler l'interface Web (React / Vite) si c'est le premier lancement.
- Lancer le simulateur physique PyBullet dans une fenêtre (le robot apparaîtra stabilisé au sol).
- Lancer le serveur Central CORE avec tous ses modules dans un autre terminal.

Une fois lancé, ouvrez [http://localhost:8000](http://localhost:8000) dans votre navigateur web pour accéder au Dashboard live !

### 3. Lancement Manuel (Nœuds séparés)
Si vous répartissez la charge sur plusieurs ordinateurs :
- **Hub & IA** : `python main.py --role all`
- **Simulateur 3D** : `python simulation/quadruped_pybullet_option_2.py`

---

## 🎮 Comment Tester la Simulation ?
Dans le dashboard Web ou via commande vocale, incitez l'IA à avancer en disant par exemple :
> *"Il y a quelqu'un devant toi, avance lui dire bonjour !"*

L'intention est retranscrite en commande `[CMD: avancer]`, envoyée silencieusement au port UDP de PyBullet. **Le modèle 3D se mettra immédiatement au trot sous vos yeux !**

---

## 🛡️ Structure du Repository
- **`core/`** : Logique métier (Vision locale, IA, Serveur API, Client WebSocket).
- **`simulation/`** : Moteur PyBullet et scripts de tests d'équilibre / marche.
- **`web/`** : Code source React/Vite de l'interface graphique.
- **`robot/`** : (Optionnel) Environnement Docker ROS 2 pour le futur matériel réel (Jetson/Raspberry).

---
*Projet Bastet V2 - Développé par Teano & Gemini*
