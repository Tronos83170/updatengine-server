# Wake-on-LAN Proxy System

## Vue d'ensemble

Le système WOL Proxy permet d'étendre les capacités de réveil à distance (Wake-on-LAN) d'UpdateEngine vers des réseaux distants ou isolés qui ne sont pas directement accessibles depuis le serveur principal.

## Fonctionnalités

- **Gestion centralisée** : Configuration et gestion des serveurs proxy WOL depuis l'interface web d'UpdateEngine
- **Support multi-réseaux** : Possibilité de définir plusieurs proxies pour différents sous-réseaux
- **Routage intelligent** : Sélection automatique du proxy approprié en fonction du sous-réseau de la machine cible
- **Interface intuitive** : Formulaires simples pour ajouter, modifier et supprimer des proxies
- **Validation robuste** : Vérification des adresses IP, ports et sous-réseaux en notation CIDR

## Architecture

### Composants principaux

1. **Modèle de données** (`inventory/models.py` - WOLProxy)
   - Stocke les informations de configuration des proxies
   - Champs: nom, adresse, port, sous-réseaux, statut actif

2. **Vues Django** (`inventory/views_wol.py`)
   - `wol_proxy_list` : Liste tous les proxies configurés
   - `wol_proxy_add` : Ajoute un nouveau proxy
   - `wol_proxy_edit` : Modifie un proxy existant
   - `wol_proxy_delete` : Supprime un proxy

3. **Formulaires** (`inventory/forms_wol.py`)
   - Validation des données d'entrée
   - Vérification du format CIDR des sous-réseaux
   - Détection des doublons

4. **Templates HTML** (`inventory/templates/inventory/`)
   - `wol_proxy_list.html` : Interface de liste
   - `wol_proxy_form.html` : Formulaire d'ajout/édition

5. **URLs** (`inventory/urls_wol.py`)
   - Routes pour accéder aux différentes fonctionnalités

## Installation

### 1. Appliquer les migrations

```bash
cd /path/to/updatengine-server
python manage.py migrate inventory
```

Cela créera la table `inventory_wolproxy` dans la base de données.

### 2. Intégrer les URLs

Ajouter dans le fichier principal `urls.py` du projet :

```python
from django.urls import path, include

urlpatterns = [
    # ... autres patterns ...
    path('inventory/', include('inventory.urls_wol')),
]
```

### 3. Configurer les permissions

Ajouter les permissions appropriées dans Django Admin pour contrôler l'accès à la gestion des proxies WOL.

## Configuration d'un Proxy WOL

### Depuis l'interface web

1. Connectez-vous à UpdateEngine
2. Naviguez vers **Inventory** > **WOL Proxies**
3. Cliquez sur **Add Proxy**
4. Remplissez le formulaire :
   - **Name** : Nom descriptif du proxy (ex: "Proxy Site Distant")
   - **Address** : Adresse IP ou nom d'hôte du serveur proxy
   - **Port** : Port du service WOL (défaut: 9)
   - **Subnets** : Liste des sous-réseaux en notation CIDR (ex: 192.168.1.0/24, 10.0.0.0/8)
   - **Active** : Cochez pour activer le proxy
5. Cliquez sur **Save**

### Format des sous-réseaux

Les sous-réseaux doivent être spécifiés en notation CIDR, séparés par des virgules :

```
192.168.1.0/24, 192.168.2.0/24, 10.0.0.0/16
```

## Utilisation

### Réveil d'une machine via proxy

Lorsqu'UpdateEngine doit réveiller une machine :

1. Le système identifie le sous-réseau de la machine cible
2. Il recherche un proxy WOL actif gérant ce sous-réseau
3. Si un proxy est trouvé, la commande WOL est envoyée au proxy
4. Le proxy transmet le paquet magique WOL à la machine cible
5. Si aucun proxy n'est trouvé, la commande est envoyée directement (comportement par défaut)

### Exemple de flux

```
UpdateEngine Server (10.1.0.10)
    |
    | Machine cible: 192.168.50.25
    | Détection: nécessite proxy pour 192.168.50.0/24
    |
    v
WOL Proxy (192.168.50.1)
    |
    | Envoi du paquet magique
    |
    v
Machine Cible (192.168.50.25) - SE RÉVEILLE
```

## Configuration du Serveur Proxy

### Prérequis

- Python 3.x
- Accès réseau au sous-réseau cible
- Permissions pour envoyer des paquets UDP

### Script Proxy WOL (à déployer sur chaque serveur proxy)

Créer un fichier `wol_proxy_service.py` sur le serveur proxy :

```python
#!/usr/bin/env python3
import socket
import struct
import sys

def send_magic_packet(mac_address, broadcast_ip='255.255.255.255', port=9):
    """
    Envoie un paquet magique WOL
    """
    # Nettoyer l'adresse MAC
    mac = mac_address.replace(':', '').replace('-', '')
    
    if len(mac) != 12:
        raise ValueError('Adresse MAC invalide')
    
    # Créer le paquet magique
    data = bytes.fromhex('FF' * 6 + mac * 16)
    
    # Envoyer le paquet
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    sock.sendto(data, (broadcast_ip, port))
    sock.close()

def start_proxy_server(listen_port=9):
    """
    Démarre le serveur proxy WOL
    """
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind(('0.0.0.0', listen_port))
    
    print(f'WOL Proxy listening on port {listen_port}')
    
    while True:
        data, addr = sock.recvfrom(1024)
        # Format attendu: MAC_ADDRESS,BROADCAST_IP
        try:
            message = data.decode('utf-8').strip()
            parts = message.split(',')
            mac = parts[0]
            broadcast = parts[1] if len(parts) > 1 else '255.255.255.255'
            
            print(f'Received WOL request for {mac} from {addr}')
            send_magic_packet(mac, broadcast)
            print(f'Magic packet sent for {mac}')
        except Exception as e:
            print(f'Error processing request: {e}')

if __name__ == '__main__':
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 9
    start_proxy_server(port)
```

### Déploiement du service

#### Systemd (Linux)

Créer `/etc/systemd/system/wol-proxy.service` :

```ini
[Unit]
Description=Wake-on-LAN Proxy Service
After=network.target

[Service]
Type=simple
User=wolproxy
WorkingDirectory=/opt/wol-proxy
ExecStart=/usr/bin/python3 /opt/wol-proxy/wol_proxy_service.py 9
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Activer et démarrer :

```bash
sudo systemctl daemon-reload
sudo systemctl enable wol-proxy
sudo systemctl start wol-proxy
```

## Dépannage

### Le proxy n'apparaît pas dans la liste

- Vérifiez que les migrations ont été appliquées
- Vérifiez les logs Django pour les erreurs

### Les machines ne se réveillent pas

1. Vérifiez que le proxy est actif dans l'interface
2. Vérifiez que le sous-réseau est correctement configuré
3. Vérifiez que le service proxy est en cours d'exécution
4. Vérifiez les règles de pare-feu (port UDP 9)
5. Vérifiez que le Wake-on-LAN est activé dans le BIOS de la machine cible

### Logs

Consulter les logs Django :

```bash
tail -f /var/log/updatengine/updatengine.log
```

Consulter les logs du proxy :

```bash
sudo journalctl -u wol-proxy -f
```

## Sécurité

### Recommandations

- Utilisez un pare-feu pour limiter l'accès au port du proxy
- Authentification entre UpdateEngine et les proxies (à implémenter)
- Chiffrement des communications (à implémenter)
- Limitation du taux de requêtes

### Restrictions réseau

Le serveur UpdateEngine doit pouvoir atteindre chaque proxy WOL sur le port configuré (défaut: 9).

## Évolutions futures

- [ ] Authentification des proxies
- [ ] Chiffrement des communications
- [ ] Monitoring de l'état des proxies
- [ ] Statistiques d'utilisation
- [ ] Support IPv6
- [ ] Interface REST API
- [ ] Auto-découverte des proxies

## Support

Pour toute question ou problème :

- Consultez la documentation officielle d'UpdateEngine
- Ouvrez une issue sur GitHub
- Contactez l'équipe de support

## Licence

Ce module est distribué sous licence GPL-2.0, comme le projet UpdateEngine principal.
