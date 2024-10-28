import random

class WhiteBoxProtocol:
    def __init__(self, myip):
        self.myip = myip
        self.processed_tags = set()  # Tags déjà traités
        self.network = []  # Liste des nœuds voisins
        self.good_deal_table = {}  # Table des bonnes affaires

    def new_tag(self, ipsend):
        """Génère un nouveau tag unique basé sur l'adresse d'envoi."""
        return f"{ipsend}-{random.randint(1000, 9999)}"

    def game_over(self, tag):
        """Détermine si la recherche est terminée pour le tag donné."""
        return tag in self.processed_tags

    def push_tag(self, tag):
        """Ajoute un tag à la liste des tags traités."""
        self.processed_tags.add(tag)

    def is_responsible(self, net, key):
        """Détermine si le réseau est responsable de la clé donnée."""
        # Pour simplification, on dit que ce nœud est responsable
        return hash(key) % len(self.network) == self.network.index(net)

    def good_deal(self, net, ipsend):
        """Détermine si le réseau/ipsend est une 'bonne affaire'."""
        # Implémentation simplifiée : considérer aléatoirement que c'est une bonne affaire
        return random.choice([True, False])

    def next_hop(self, key):
        """Détermine le prochain nœud à contacter en fonction de la clé."""
        return self.network[hash(key) % len(self.network)]

    def distrib_mrr(self, mrr):
        """Répartit le taux de réplication maximum parmi les réseaux."""
        # Divise le MRR de manière égale entre tous les réseaux
        return {net: mrr / len(self.network) for net in self.network}

    def ope(self, code, key, value, ipsend):
        """Traite une opération OPE."""
        tag = self.new_tag(ipsend)
        self.find(code, ttl=10, mrr=10, tag=tag, key=key, value=value, ipdest=self.myip)

    def find(self, code, ttl, mrr, tag, key, value, ipdest):
        """Traite un message FIND."""
        if ttl == 0 or self.game_over(tag):
            print(f"Recherche abandonnée TTL = {ttl}, messsage traité = {self.game_over(tag)}")
            return

        self.push_tag(tag)
        next_mrr = self.distrib_mrr(mrr)

        for net in self.network:
            if self.is_responsible(net, key):
                self.found(code, net, mrr, key, value, ipdest)
            elif self.good_deal(net, ipdest):
                next_hop = self.next_hop(key)
                print(f"Envoi du message FIND vers {next_hop}")
                self.find(code, ttl - 1, next_mrr[net], tag, key, value, next_hop)

    def found(self, code, net, mrr, key, value, ipsend):
        """Traite un message FOUND."""
        self.good_deal_update(net, ipsend)
        if code == "GET":
            self.read_table(net, key, ipsend)
        elif code == "PUT":
            if mrr < 0:
                print("Arrêt de la réplication (MRR < 0).")
            else:
                self.write_table(net, key, value, ipsend)

    def good_deal_update(self, net, ipsend):
        """Mise à jour de la table des bonnes affaires."""
        self.good_deal_table[net] = ipsend

    def read_table(self, net, key, ipsend):
        """Lecture de la valeur associée à la clé dans le réseau."""
        print(f"Lecture de la clé {key} sur le réseau {net} depuis {ipsend}.")

    def write_table(self, net, key, value, ipsend):
        """Écriture de la valeur associée à la clé dans le réseau."""
        print(f"Écriture de la clé {key} avec la valeur {value} sur le réseau {net} depuis {ipsend}.")

    def invite(self, net, ipsend):
        """Traite un message INVITE pour rejoindre un réseau."""
        if self.good_deal(net, ipsend):
            self.join(net, ipsend)

    def join(self, net, ipsend):
        """Rejoint un réseau."""
        print(f"Rejoindre le réseau {net} depuis {ipsend}.")
        self.insert_net(net, ipsend)

    def insert_net(self, net, ipsend):
        """Ajoute un nœud au réseau."""
        if net not in self.network:
            self.network.append(net)
            print(f"Nœud {ipsend} ajouté au réseau {net}.")

# Exemple d'utilisation
protocol = WhiteBoxProtocol("192.168.1.1")
protocol.network = ["192.168.1.2", "192.168.1.3", "192.168.1.4"]

# Lancement d'une opération OPE de type GET
protocol.ope("GET", "clé1", None, "192.168.1.100")

# Lancement d'une opération OPE de type PUT
protocol.ope("PUT", "clé2", "valeur2", "192.168.1.101")
