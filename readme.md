# Mesh Creator

## Installation des libraries
• Créer un environnement virtuel python

``$ python3 -m venv .venv``

• Activer l'environnement virtuel

``$ source .venv/bin/activate``

• Installer les lib python du requirements.txt

``$ pip install -r requirements.txt``

## Lancer le créateur
• Ouvrir un terminal dans le dossier de l'éditeur et lancer la commande suivante :

``$ python3 editor.py``

• Pour lancer l'éditeur avec une forme déja construite (.geo et .geo_unrolled) :

``$ python3 editor.py <chemin>``

## Fonctionnement
*Les touches présentées ici sont celles utilisées par défaut*
### Points
• **Clic gauche** : Ajout d'un point\
• **Clic droit** : Retire le dernier point de la figure en cours

### Modes
• **'R'** : Basculer entre le mode 'ligne' et 'arc de cercle'

### Ancrage
• **'Z'** : Basculer l'ancrage en mode Grand -> Moyen -> Petit -> Désactivé\
• **SHIFT + 'Z'** : Basculer l'ancrage en mode Grand <- Moyen <- Petit <- Désactivé

### Gestion des figures
• **'E'** : Nouvelle figure\
• **'up'** : Figure suivante\
• **'down'** : Figure précédente

### Sauvegardes
#### > .msh
• **'S'** : Sauvegarde en .msh\
• **SHIFT + 'S'** : Sauvegarde en .msh (avec subdivision)

#### > .geo
• **'G'**: Sauvegarde en .geo

### Visualisation
• **'V'** : Visualiser sous GMSH\
• **SHIFT + 'V'** Visualiser sous GMSH (avec subdivision)

### Gestion des algorithmes
• **'A'** : Changer d'algorithme (affiche l'algoritme en cours dans la console)

## /!\
Le but ici est de créer la forme globale et pas directement le maillage. 

Le maillage est généré automatiquement par la bibliothèque ***gmsh***