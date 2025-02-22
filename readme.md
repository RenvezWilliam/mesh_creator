# Mesh Creator

## Installation des libraries
• Créer un environnement virtuel python

``$ python3 -m venv .venv``

• Activer l'environnement virtuel

``$ source .venv/bin/activate``

• Installer les lib python du requirements.txt

``$ pip install -r requirements.txt``

## Lancer le créateur
• Ouvrir un terminal dans le dossier du créateur et lancer la commande suivante :

``$ python3 creator.py``

## Fonctionnement

### Points
• **Clic gauche** : Ajout d'un point\
• **Clic droit** : Retire le dernier point de la figure en cours

### Ancrage
• **CTRL** : Grand ancrage\
• **SHIFT** : Moyen ancrage\
• **CTRL + SHIFT** : Petit ancrage

### Gestion des figures
• **'N'** : Nouvelle figure\
• **'🠕'** : Figure suivante\
• **'🠗'** : Figure précédente

### Sauvegardes
#### > .msh
• **'S'** : Sauvegarde en .msh\
• **SHIFT + 'S'** : Sauvegarde en .msh (avec subdivision)

#### > .geo
• ***Work In Progress***

### Visualisation
• **'V'** : Visualiser sous GMSH\
• **SHIFT + 'V'** Visualiser sous GMSH (avec subdivision)

### Gestion des algorithmes
• **'A'** : Changer d'algorithme (affiche l'algoritme en cours dans la console)

## /!\
Le but ici est de créer la forme globale et pas directement le maillage. 

Le maillage est généré automatiquement par la bibliothèque ***gmsh***