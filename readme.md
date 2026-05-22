# 🏹 Hunt the Wumpus

Une adaptation moderne sous forme d'application web Flask du jeu de texte classique **Hunt the Wumpus** (Chasse au Wumpus). Explorez un réseau de cavernes interconnectées, évitez les pièges mortels et traquez le redoutable Wumpus !

## Installation

```bash
   git clone https://github.com/NextSap/hunt-the-wumpus.git
   cd hunt-the-wumpus
   pip install -r requirements.txt
```

## Configuration
1. Créer un fichier config.py à la racine du projet.
2. Ajouter les variables d'environnement suivantes :
```
SECRET_KEY=""
DB_USER=""
DB_PASSWORD=""
DB_NAME=""
DB_HOST=""
DB_PORT=
```

## Run
```
flask run --port=8080
```