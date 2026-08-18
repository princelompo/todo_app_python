# ============================================
# manager.py — Logique métier
# ============================================
#
# Ce module implémente la logique métier de l'application.
# Il fournit une interface de haut niveau pour gérer les tâches,
# encapsulant les opérations de base de données et la validation.
#
# Responsabilités :
#   - Validation des données avant insertion/modification
#   - Gestion des erreurs métier (todo introuvable, etc.)
#   - Ordonner les opérations de base de données
#   - Mettre en œuvre les règles métier (ex: un todo terminé ne peut pas être retouché)
#
# Relation avec Database :
#   TodoManager utilise Database pour l'accès aux données
#   Database est une couche d'abstraction pour SQLite
#
# ============================================

from database import Database
from todo import Todo


class TodoManager:
    """
    Orchestre toutes les opérations sur les todos.
    
    Fournit une interface de haut niveau pour :
      - Créer, lire, modifier, supprimer des tâches
      - Valider les données d'entrée
      - Appliquer la logique métier
      - Gérer les erreurs et exceptions
    
    Attributs :
        db (Database): Instance de Database pour l'accès aux données
    """

    def __init__(self):
        """
        Initialise le gestionnaire de tâches.
        
        Crée une instance de Database qui gère la persistance des données.
        """
        # Crée une instance de la couche d'accès aux données
        self.db = Database()

    def ajouter(self, titre, description="",
                priorite="moyenne", categorie="autre"):
        """
        Crée et sauvegarde une nouvelle tâche.
        
        Valide le titre avant création et assigne l'ID retourné par la BD.
        
        Args :
            titre (str): Titre de la tâche (obligatoire)
            description (str): Description détaillée (défaut: "")
            priorite (str): Niveau de priorité (défaut: "moyenne")
            categorie (str): Catégorie (défaut: "autre")
        
        Returns :
            Todo: La tâche créée avec son ID assigné
        
        Raises :
            ValueError: Si le titre est vide ou ne contient que des espaces
        """
        # Valide que le titre n'est pas vide (validation métier)
        if not titre.strip():
            raise ValueError("Le titre ne peut pas être vide !")

        # Crée un nouvel objet Todo en mémoire
        todo    = Todo(titre, description, priorite, categorie)
        # Insère la tâche dans la BD et assigne son ID auto-généré
        todo.id = self.db.ajouter(todo)
        # Retourne la tâche avec son ID
        return todo

    def terminer(self, todo_id):
        """
        Marque une tâche comme terminée.
        
        Validation :
          - Vérifie que la tâche existe
          - Vérifie qu'elle n'est pas déjà terminée
        
        Args :
            todo_id (int): ID de la tâche à terminer
        
        Returns :
            Todo: La tâche avant modification (à titre informatif)
        
        Raises :
            ValueError: Si la tâche n'existe pas ou est déjà terminée
        """
        # Récupère la tâche de la BD
        todo = self.db.trouver(todo_id)
        # Vérifie que la tâche existe
        if not todo:
            raise ValueError(f"Todo #{todo_id} introuvable !")
        # Vérifie qu'elle n'est pas déjà terminée (validation métier)
        if todo.termine:
            raise ValueError(f"Todo #{todo_id} est déjà terminé !")
        # Met à jour le statut dans la BD
        self.db.modifier(todo_id, termine=1)
        # Retourne l'objet avant modification
        return todo

    def rouvrir(self, todo_id):
        """
        Rouvre une tâche terminée pour la rendre à nouveau active.
        
        Args :
            todo_id (int): ID de la tâche à rouvrir
        
        Returns :
            Todo: La tâche avec le nouveau statut
        
        Raises :
            ValueError: Si la tâche n'existe pas
        """
        # Récupère la tâche de la BD
        todo = self.db.trouver(todo_id)
        # Vérifie que la tâche existe
        if not todo:
            raise ValueError(f"Todo #{todo_id} introuvable !")
        # Marque la tâche comme non terminée dans la BD
        self.db.modifier(todo_id, termine=0)
        # Retourne la tâche modifiée
        return todo

    def modifier(self, todo_id, **champs):
        """
        Modifie une tâche existante.
        
        Args :
            todo_id (int): ID de la tâche à modifier
            **champs: Champs à modifier (titre, priorite, description, etc.)
        
        Returns :
            Todo: La tâche modifiée avec les nouvelles valeurs
        
        Raises :
            ValueError: Si la tâche n'existe pas
        
        Exemple :
            manager.modifier(1, titre="Nouveau titre", priorite="haute")
        """
        # Récupère la tâche de la BD pour vérifier son existence
        todo = self.db.trouver(todo_id)
        # Vérifie que la tâche existe
        if not todo:
            raise ValueError(f"Todo #{todo_id} introuvable !")
        # Modifie les champs spécifiés dans la BD
        self.db.modifier(todo_id, **champs)
        # Récupère et retourne la tâche modifiée
        return self.db.trouver(todo_id)

    def supprimer(self, todo_id):
        """
        Supprime définitivement une tâche.
        
        Args :
            todo_id (int): ID de la tâche à supprimer
        
        Returns :
            Todo: La tâche supprimée (pour confirmation/affichage)
        
        Raises :
            ValueError: Si la tâche n'existe pas
        """
        # Récupère la tâche avant suppression (pour retour d'info)
        todo = self.db.trouver(todo_id)
        # Vérifie que la tâche existe
        if not todo:
            raise ValueError(f"Todo #{todo_id} introuvable !")
        # Supprime la tâche de la BD
        self.db.supprimer(todo_id)
        # Retourne la tâche supprimée (à titre informatif)
        return todo

    def lister(self, filtre=None):
        """
        Retourne une liste filtrée des tâches.
        
        Délègue à Database.tous() pour le filtrage.
        
        Filtres supportés :
          - "actifs" : tâches non terminées
          - "termines" : tâches terminées
          - <categorie> : par catégorie
          - <priorite> : par priorité
          - None : toutes les tâches
        
        Args :
            filtre (str): Type de filtre optionnel
        
        Returns :
            list: Liste de tous les todos (objets Todo) selon le filtre
        """
        # Délègue le filtrage à la couche BD
        return self.db.tous(filtre)

    def statistiques(self):
        """
        Retourne les statistiques globales des tâches.
        
        Délègue à Database.statistiques() pour le calcul.
        
        Returns :
            dict: Dictionnaire contenant :
                - "total" : nombre total de tâches
                - "termines" : nombre de tâches complétées
                - "actifs" : nombre de tâches en cours
        """
        # Délègue le calcul des statistiques à la couche BD
        return self.db.statistiques()