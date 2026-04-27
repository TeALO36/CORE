\# SpotBot — SpotMicro AI Build Pack



> Archive complète pour construire le robot quadrupède SpotMicro.  

> Sources récupérées depuis GitHub et Thingiverse — GitLab original `custom\_robots/spotmicroai` inaccessible.



\---



\## Contenu du dossier `D:\\dl\\SpotBot\\`



\### Modèles 3D à imprimer



| Fichier | Taille | Description |

|---------|--------|-------------|

| `Spotmicro - robot dog - 3445283 - part 1 of 2.zip` | \~17 Mo | STL officiels SpotMicro par KDY0523 — parties 1/2 |

| `Spotmicro - robot dog - 3445283 - part 2 of 2.zip` | \~5 Mo | STL officiels SpotMicro par KDY0523 — parties 2/2 |



\- \*\*Source :\*\* \[Thingiverse thing:3445283](https://www.thingiverse.com/thing:3445283) par KDY0523

\- \*\*Licence :\*\* Creative Commons Attribution (CC BY)

\- \*\*84 fichiers STL\*\* au total — extraire les deux ZIPs dans le même dossier

\- Robot : 4 pattes, 3 servos par patte = \*\*12 servos MG996R\*\*, châssis imprimable en PLA/PETG

\- Dimensions : \~300 mm de long



\---



\### Code source — Simulation



\#### `spot\_mini\_mini-spot.zip` (\~557 Mo)

\- \*\*Source :\*\* \[github.com/OpenQuadruped/spot\_mini\_mini](https://github.com/OpenQuadruped/spot\_mini\_mini) — branche `spot`

\- \*\*Simulation PyBullet\*\* (sans ROS obligatoire) + environnement \*\*OpenAI Gym\*\*

\- Gait Bezier 12 points, \*\*Reinforcement Learning (ARS)\*\*, GUI avec sliders

\- Contrôle \*\*ROS + joystick\*\* via `roslaunch mini\_ros spot\_move.launch`

\- Modèle redessiné OpenQuadruped (URDF haute fidélité physique)

\- Agents pré-entraînés inclus (`spot\_best.zip` — agent #2229 recommandé)

\- \*\*Dépendances :\*\* Python 3, PyBullet, Gym, NumPy, SciPy, PyTorch, OpenCV, ROS Noetic/Melodic



\*\*Lancement rapide (sans ROS) :\*\*

```bash

cd spot\_mini\_mini-spot/spot\_bullet/src

pip install pybullet numpy scipy opencv-python gym torch

./env\_tester.py

```



\#### `spot\_mini\_mini-spotmicroai.zip` (\~264 Mo)

\- \*\*Source :\*\* \[github.com/OpenQuadruped/spot\_mini\_mini](https://github.com/OpenQuadruped/spot\_mini\_mini) — branche `spotmicroai`

\- Même simulateur PyBullet/ROS mais avec l'\*\*URDF SpotMicro original\*\* (compatible avec les STL de Thingiverse ci-dessus)

\- À utiliser si tu veux simuler exactement le robot physique que tu imprimes



\#### `spotmicro-main.zip` (\~3,3 Mo)

\- \*\*Source :\*\* \[github.com/sulibo/spotmicro](https://github.com/sulibo/spotmicro)

\- Miroir GitHub du dépôt simulation original du GitLab SpotMicroAI

\- Simulation \*\*Gazebo + RViz\*\* via ROS

\- URDF + packages ROS complets, proche de la version GitLab officielle

\- \*\*Dépendances :\*\* ROS Noetic/Melodic, Gazebo



\*\*Lancement :\*\*

```bash

cd spotmicro-main

catkin build

source devel/setup.bash

roslaunch spotmicro\_description spotmicro\_display.launch

```



\---



\### Code source — Basic Build (robot physique)



\#### `spotMicro-master.zip` (\~25 Mo)

\- \*\*Source :\*\* \[github.com/mike4192/spotMicro](https://github.com/mike4192/spotMicro)

\- Code pour faire \*\*marcher le vrai robot\*\* imprimé en 3D

\- \*\*ROS\*\* + contrôle des 12 servos via \*\*PCA9685\*\* (I2C) sur \*\*Raspberry Pi\*\*

\- Contrôle clavier (`spotMicroKeyboardMove.py`) et support manette

\- Cinématique inverse complète, démarche programmée

\- Compatible à 100% avec les STL KDY0523 de Thingiverse

\- \*\*Dépendances :\*\* ROS Noetic/Melodic, `i2cpwm\_board`, `libi2c-dev`, Python 3



\*\*Lancement sur Raspberry Pi :\*\*

```bash

cd spotMicro-master

git submodule update --init --recursive

catkin config --cmake-args -DCMAKE\_BUILD\_TYPE=Release

catkin build spot\_micro\_motion\_cmd

source devel/setup.bash

\# Terminal 1

rosrun i2cpwm\_board i2cpwm\_board

\# Terminal 2

roslaunch spot\_micro\_motion\_cmd motion\_cmd.launch run\_standalone:=true

\# Terminal 3

rosrun spot\_micro\_keyboard\_command spotMicroKeyboardMove.py

```



\---



\## Architecture du projet



