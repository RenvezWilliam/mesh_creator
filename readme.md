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
• **Clique souris** : Ajout d'un point

• **Maintenir CTRL** : Grand ancrage

• **Maintenir SHIFT** : Moyen ancrage

• **Maintenir CTRL + SHIFT** : Petit ancrage

• **Bouton 'R'** : Retire le dernier point

• **Bouton 'S'** : Sauvegarde en un fichier .msh

## /!\
Le but ici est de créer la forme globale et pas directement le maillage. 

Le maillage est généré automatiquement par la bibliothèque ***gmsh***