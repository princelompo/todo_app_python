# ============================================
# todo.py — Classe Todo (modèle de données)
# ============================================
#
# Ce module définit la structure de base d'une tâche (Todo).
# Il contient la classe Todo qui représente un élément individuel
# dans la liste de tâches de l'utilisateur.
#
# Responsabilités :
#   - Définir les attributs d'une tâche
#   - Valider les priorités et catégories
#   - Convertir entre objets Todo et dictionnaires
#   - Fournir une représentation textuelle formatée
#
# ============================================

from datetime import datetime


class Todo:
    """
    Représente une tâche dans l'application.
    
    Attributs :
        id (int): Identifiant unique de la tâche (assigné par la BD)
        titre (str): Titre/nom de la tâche
        description (str): Description détaillée optionnelle
        priorite (str): Priorité parmi ['basse', 'moyenne', 'haute']
        categorie (str): Catégorie parmi ['travail', 'personnel', 'études', 'autre']
        termine (bool): Indique si la tâche est complétée
        date_creation (str): Timestamp de création au format "JJ/MM/YYYY HH:MM"
    """

    # Énumération des priorités possibles pour une tâche
    PRIORITES = ["basse", "moyenne", "haute"]

    # Énumération des catégories possibles pour une tâche
    CATEGORIES = ["travail", "personnel", "études", "autre"]

    def __init__(self, titre, description="", priorite="moyenne",
                 categorie="autre", id=None, termine=False,
                 date_creation=None):
        """
        Initialise une nouvelle tâche.
        
        Args :
            titre (str): Le titre de la tâche (obligatoire)
            description (str): Description détaillée (défaut: vide)
            priorite (str): Niveau de priorité (défaut: "moyenne")
            categorie (str): Catégorie de la tâche (défaut: "autre")
            id (int): ID de la tâche (défaut: None, assigné par BD)
            termine (bool): Statut d'achèvement (défaut: False)
            date_creation (str): Timestamp de création (défaut: maintenant)
        """
        # Identifiant unique (None avant insertion en BD)
        self.id           = id
        # Titre de la tâche
        self.titre        = titre
        # Description détaillée de la tâche
        self.description  = description
        # Validation et assignation de la priorité avec fallback
        self.priorite     = priorite if priorite in self.PRIORITES else "moyenne"
        # Validation et assignation de la catégorie avec fallback
        self.categorie    = categorie if categorie in self.CATEGORIES else "autre"
        # Statut d'achèvement de la tâche
        self.termine      = termine
        # Timestamp de création (assigné maintenant si non fourni)
        self.date_creation = date_creation or datetime.now().strftime("%d/%m/%Y %H:%M")

    def to_dict(self):
        """
        Convertit l'objet Todo en dictionnaire.
        
        Utilisé pour la sérialisation vers la base de données.
        
        Returns :
            dict: Dictionnaire contenant tous les attributs de la tâche
        """
        return {
            "id":            self.id,
            "titre":         self.titre,
            "description":   self.description,
            "priorite":      self.priorite,
            "categorie":     self.categorie,
            "termine":       self.termine,
            "date_creation": self.date_creation
        }

    @classmethod
    def from_dict(cls, data):
        """
        Crée une instance Todo à partir d'un dictionnaire.
        
        Utilisé pour la désérialisation depuis la base de données.
        
        Args :
            data (dict): Dictionnaire contenant les données de la tâche
        
        Returns :
            Todo: Une nouvelle instance Todo avec les données du dictionnaire
        """
        # Crée une nouvelle instance Todo avec les données fournies
        # Utilise .get() pour gérer les clés manquantes avec des valeurs par défaut
        return cls(
            id           = data.get("id"),
            titre        = data["titre"],  # Obligatoire
            description  = data.get("description", ""),  # Défaut: vide
            priorite     = data.get("priorite", "moyenne"),  # Défaut: moyenne
            categorie    = data.get("categorie", "autre"),  # Défaut: autre
            termine      = bool(data.get("termine", False)),  # Défaut: non terminé
            date_creation= data.get("date_creation")  # Défaut: None
        )

    def __str__(self):
        """
        Retourne une représentation textuelle formatée de la tâche.
        
        Affiche :
          - Statut (✅ terminée, ⬜ en cours)
          - ID de la tâche entre crochets
          - Titre de la tâche
          - Indicateur visuel de priorité (🟢 basse, 🟡 moyenne, 🔴 haute)
          - Catégorie entre parenthèses
        
        Returns :
            str: Représentation formatée de la tâche pour l'affichage
        
        Exemple :
            ✅ [1] Faire les courses 🟢 (personnel)
        """
        # Symbole emoji du statut : ✅ si terminée, ⬜ si active
        statut   = "✅" if self.termine else "⬜"
        # Dictionnaire de mapping entre priorité et emoji indicateur
        priorite = {"basse": "🟢", "moyenne": "🟡", "haute": "🔴"}
        # Construction et retour de la chaîne formatée
        return (f"{statut} [{self.id}] {self.titre} "
                f"{priorite.get(self.priorite, '')} "
                f"({self.categorie})")