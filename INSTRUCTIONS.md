# Flappy Bird avec MongoDB Atlas - Instructions

Ce jeu Flappy Bird a été modifié pour se connecter directement à MongoDB Atlas afin de stocker les scores des joueurs dans une base de données cloud.

## Installation

1. Assurez-vous d'avoir Python 3.6+ installé sur votre système
2. Clonez ou téléchargez ce dépôt
3. Installez les dépendances requises :

```bash
pip install -r requirements.txt
```

## Lancement du jeu

Pour lancer le jeu, exécutez simplement :

```bash
python run.py
```

## Résolution des problèmes de connexion

Si vous rencontrez des erreurs de connexion à MongoDB Atlas (erreurs SSL), voici quelques solutions :

### 1. Problèmes réseau

- Assurez-vous d'avoir une connexion Internet stable
- Vérifiez que votre réseau n'a pas de restrictions (pare-feu d'entreprise/école)
- Essayez de vous connecter via un autre réseau (par exemple, utiliser les données mobiles au lieu du Wi-Fi)

### 2. Mettre à jour les bibliothèques Python

```bash
pip install --upgrade pymongo certifi
```

### 3. Mode hors ligne

Le jeu est conçu pour fonctionner même sans connexion à MongoDB Atlas. Dans ce cas :

- Les scores seront stockés localement pendant votre session de jeu
- Les scores ne seront pas partagés avec d'autres joueurs
- Les scores ne seront pas persistants entre les sessions

## Fonctionnement

- Le jeu se connecte directement à MongoDB Atlas pour stocker et récupérer les scores
- Un système de mise en cache réduit les requêtes à la base de données
- Des threads sont utilisés pour les opérations de base de données afin de ne pas bloquer le jeu

## Remarques importantes

- Les identifiants MongoDB sont déjà configurés dans le code
- Tous les joueurs partagent la même base de données, créant ainsi un classement global
- Le jeu fonctionne même sans connexion Internet, mais les scores ne seront pas enregistrés dans la base de données cloud

## Développement

Si vous souhaitez lancer le backend FastAPI séparément (pour l'interface web du leaderboard) :

```bash
python -m uvicorn fastapi_backend:app --reload
```

Vous pourrez alors accéder au leaderboard via http://localhost:8000
