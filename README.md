
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

# Installation locale


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


### Lancement local

**Docker**
```bash
sudo docker-compose up --build -d
```

### Invitation de votre bot local

1. Sur la page Discord Dev Portal, vous pouvez naviguez dans la section `Installation` et ouvrir l'URL d'invitation donnée


# Inviter le bot public à un serveur discord

Cliquer sur cet URL et ajouter le bot au serveur désiré (connectez vous à votre compte discord si nécessaire). 
1. https://discord.com/oauth2/authorize?client_id=1177896807267835984

Attention, si vous voulez inviter votre propre instance du Guide Du Rootard, vous devez générer par vous même le lien d'invitation.


### Mis en place sur Discord

1. Créer un canal `leguidedurootard-admin`
2. Créer un canal `leguidedurootard-scoreboard`
3. Créer un canal `leguidedurootard-notifications`
4. Dans `leguidedurootard-admin` tapez `/setAdminChannel`
5. Dans `leguidedurootard-admin` tapez `/enableGlobalNotifications leguidedurootard-notifications`
6. Dans `leguidedurootard-admin` tapez `/enableGlobalScoreboard leguidedurootard-scoreboard`

### Manager les utlisateurs

1. Pour ajouter un utilisateur, naviguez dans `leguidedurootard-admin` et tapez `/addUser USERNAME`. (Attention, le USERNAME est le pseudo public, i.e. celui qui est après le / derrière l'URL de vôtre profil public. Par exemple, mon profil public est https://www.root-me.org/Neoreo alors le USERNAME est Neoreo. Cela permet d'identifier de manière unique les utilisateurs avec un pseudo doublon)

2. Pour supprimer un utlisateur, naviguez dans `leguidedurootard-admin` et saisissez `/removeUser USERNAME`, cette fois encore avec le USERNAME public.

