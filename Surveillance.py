import subprocess
import time
import socket
from datetime import datetime

import mysql.connector

# Fonction pour obtenir l'adresse IP actuelle
def obtenir_adresse_IP_actuelle():
    try:
        return socket.gethostbyname(socket.gethostname())
    except socket.gaierror:
        return None

# Fonction pour collecter les adresses IP
def collecter_adresses_IP():
    try:
        # Exécuter la commande arp -a pour obtenir les adresses IP associées aux adresses MAC
        result = subprocess.check_output(['arp', '-a'], universal_newlines=True)
        
        # Diviser la sortie en lignes
        lines = result.splitlines()
        
        # Parcourir chaque ligne pour extraire les adresses IP
        adresses_IP = []
        for line in lines:
            # Diviser la ligne en mots
            words = line.split()
            if len(words) >= 2:
                # Le deuxième élément contient l'adresse IP
                adresse_IP = words[1]
                # Vérifier si l'adresse IP est valide et l'ajouter à la liste
                if '.' in adresse_IP:
                    adresses_IP.append(adresse_IP)
        
        return adresses_IP
        
    except subprocess.CalledProcessError as e:
        print("Une erreur s'est produite lors de l'exécution de la commande arp.")
        print("Erreur :", e)
        return []

# Fonction pour insérer les adresses IP dans la base de données MySQL
def inserer_adresses_IP(adresses_IP):
    try:
        # Se connecter à la base de données MySQL
        conn = mysql.connector.connect(
            host="localhost",
            user="root",
            password="",
            database="sprojet",
            ssl_disabled=True  # Désactiver SSL pour cet exemple
        )
        
        # Créer un curseur pour exécuter des requêtes SQL
        cursor = conn.cursor()
        
        # Vérifier si des adresses IP ont été collectées
        if not adresses_IP:
            print("Aucune adresse IP n'a été collectée.")
            return
        
        # Boucler sur les adresses IP collectées et les insérer dans la base de données
        for adresse_IP in adresses_IP:
            # Requête SQL pour insérer l'adresse IP et la date de collecte dans la table adresses_ip
            sql = "INSERT INTO adresses_ip (adresse_ip, date_collecte) VALUES (%s, %s)"
            # Données à insérer : adresse IP et date actuelle
            values = (adresse_IP, datetime.now())
            # Exécuter la requête SQL avec les données
            cursor.execute(sql, values)
        
        # Valider les modifications et fermer la connexion
        conn.commit()
        cursor.close()
        conn.close()
        
        print("Adresses IP insérées avec succès dans la base de données.")
        
    except mysql.connector.Error as e:
        print("Une erreur s'est produite lors de l'insertion des adresses IP dans la base de données.")
        print("Erreur :", e)

# Initialisation de l'adresse IP précédente à None
adresse_IP_precedente = None

# Boucle principale
execution_en_cours = True
while execution_en_cours:
    try:
        # Obtenir l'adresse IP actuelle
        adresse_IP_actuelle = obtenir_adresse_IP_actuelle()

        # Si l'adresse IP actuelle est différente de la précédente
        if adresse_IP_actuelle != adresse_IP_precedente:
            # Mise à jour de l'adresse IP précédente
            adresse_IP_precedente = adresse_IP_actuelle

            # Collecte des adresses IP
            adresses_IP_collectees = collecter_adresses_IP()

            # Si des adresses IP ont été collectées, les insérer dans la base de données
            if adresses_IP_collectees:
                inserer_adresses_IP(adresses_IP_collectees)

        # Attendre avant la prochaine itération
        time.sleep(5)
        
    except KeyboardInterrupt:
        print("Arrêt de la surveillance...")
        execution_en_cours = False