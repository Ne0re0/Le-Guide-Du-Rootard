
# Le Guide Du Rootard

# Objectifs

Ce bot discord à pour objectif de permettre aux joueurs de Root-Me de se challenger en permettant :

- D'avoir un scoreboard mis à jour automatiquement avec les joueurs ajoutés
- D'être notifié lorsqu'un joueur résout un challenge
- D'être notifié lorsqu'un joueur ajoute un challenge à Root-Me
- D'être notifié lorsqu'un joueur ajoute une solution à Root-Me

# Features

- Chaque serveur discord est indépendant et possède sa propre database
- Lorsque le bot s'arrête, le simple fait de le redémarrer reprend toute activité laissée en suspend (comprendre que ça redémarre le scoreboard et les notifications automatiques s'ils étaient activés)  

# Installation


```bash
sudo apt-get update -y
sudo apt-get install git docker-compose -y
git clone https://github.com/Ne0re0/Le-Guide-Du-Rootard.git
cd Le-Guide-Du-Rootard
./installer.sh # Installer les librairies et packages
```

### Configuration

Créer le fichier `src/.env` et ajoutez votre clé API discord comme suit :
```
discord_api_key="YOUR_API_KEY_HERE"
```

### Ajouter le bot à un serveur discord

J'ai oublié comment il faut faire XD

# Lancement

**Local**
```bash
python3 start
```

**Docker**
```bash
sudo docker-compose up --build -d
```