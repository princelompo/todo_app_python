# ============================================
# database.py — Gestion de la base de données
# ============================================
#
# Ce module gère l'accès à la base de données SQLite.
# Il fournit une couche d'abstraction pour toutes les opérations CRUD
# (Create, Read, Update, Delete) sur les tâches.
#
# Responsabilités :
#   - Initialiser et créer la structure de la base de données
#   - Exécuter les requêtes SQL (INSERT, SELECT, UPDATE, DELETE)
#   - Convertir les résultats SQL en objets Todo
#   - Appliquer les filtres de recherche
#   - Fournir les statistiques globales
#
# Architecture :
#   - Utilise SQLite pour la persistance locale
#   - Tables : todos (id, titre, description, priorite, categorie, termine, date_creation)
#   - Transactions sécurisées avec gestion d'erreurs
#
# ============================================

import sqlite3
from todo import Todo


class Database:
    """
    Gère toutes les opérations SQLite pour les todos.
    
    Cette classe encapsule la logique d'accès aux données et fournit une interface
    pour les opérations CRUD sur la table todos.
    
    Attributs :
        fichier (str): Chemin du fichier de base de données SQLite
    """

    def __init__(self, fichier="todos.db"):
        """
        Initialise la connection à la base de données.
        
        Args :
            fichier (str): Nom/chemin du fichier BD SQLite (défaut: "todos.db")
        """
        # Stocke le nom du fichier de base de données
        self.fichier = fichier
        # Crée la table si elle n'existe pas (initialisation)
        self._initialiser()

    def _connexion(self):
        """
        Établit une connexion à la base de données SQLite.
        
        Configure la connexion pour retourner les résultats sous forme
        de dictionnaires plutôt que de tuples.
        
        Returns :
            sqlite3.Connection: Connexion configurée à la BD
        """
        # Crée une nouvelle connexion au fichier SQLite
        conn = sqlite3.connect(self.fichier)
        # Configure row_factory pour retourner des dictionnaires
        # Permet d'accéder aux colonnes par nom plutôt que par index
        conn.row_factory = lambda c, r: {
            col[0]: r[i] for i, col in enumerate(c.description)
        }
        return conn

    def _initialiser(self):
        """
        Crée la table "todos" si elle n'existe pas.
        
        Cette méthode est appelée au démarrage pour s'assurer que la structure
        de la base de données existe. Elle est idempotente (pas d'erreur si la
        table existe déjà).
        
        Structure de la table :
            id (INTEGER) : Clé primaire auto-incrémentée
            titre (TEXT) : Titre de la tâche (obligatoire)
            description (TEXT) : Description détaillée (défaut: "")
            priorite (TEXT) : Niveau de priorité (défaut: "moyenne")
            categorie (TEXT) : Catégorie (défaut: "autre")
            termine (INTEGER) : Statut d'achèvement 0/1 (défaut: 0)
            date_creation (TEXT) : Timestamp de création
        """
        # Ouvre une connexion persistante pour exécuter le CREATE TABLE
        with sqlite3.connect(self.fichier) as conn:
            # Crée la table seulement si elle n'existe pas
            conn.execute("""
                CREATE TABLE IF NOT EXISTS todos (
                    id            INTEGER PRIMARY KEY AUTOINCREMENT,
                    titre         TEXT    NOT NULL,
                    description   TEXT    DEFAULT '',
                    priorite      TEXT    DEFAULT 'moyenne',
                    categorie     TEXT    DEFAULT 'autre',
                    termine       INTEGER DEFAULT 0,
                    date_creation TEXT
                )
            """)
            # Valide les changements (transaction)
            conn.commit()

    def ajouter(self, todo):
        """
        Insère un nouveau todo dans la base de données.
        
        Args :
            todo (Todo): Objet Todo à insérer
        
        Returns :
            int: ID (primary key) assigné à la tâche nouvellement créée
        """
        # Ouvre une connexion persistante pour l'insertion
        with sqlite3.connect(self.fichier) as conn:
            # Crée un curseur pour exécuter la requête
            cur = conn.cursor()
            # Insère la tâche dans la table avec requête paramétrée
            # (protège contre les injections SQL)
            cur.execute("""
                INSERT INTO todos
                (titre, description, priorite, categorie, termine, date_creation)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                todo.titre, todo.description, todo.priorite,
                todo.categorie, int(todo.termine), todo.date_creation
            ))
            # Valide l'insertion (commit de la transaction)
            conn.commit()
            # Retourne l'ID auto-généré de la nouvelle tâche
            return cur.lastrowid

    def tous(self, filtre=None):
        """
        Récupère tous les todos avec filtre optionnel.
        
        Supporte plusieurs types de filtres :
          - "actifs" : uniquement les tâches non terminées
          - "termines" : uniquement les tâches terminées
          - <categorie> : par catégorie (travail, personnel, études, autre)
          - <priorite> : par priorité (basse, moyenne, haute)
          - None : toutes les tâches
        
        Args :
            filtre (str): Type de filtre à appliquer (optionnel)
        
        Returns :
            list: Liste de todos (objets Todo) triés selon le filtre
        """
        # Ouvre une connexion configurée pour retourner des dictionnaires
        with self._connexion() as conn:
            # Crée un curseur pour exécuter les requêtes
            cur = conn.cursor()

            # Sélectionne la requête SQL selon le type de filtre
            if filtre == "actifs":
                # Récupère les tâches actives (non terminées), triées par priorité
                cur.execute("SELECT * FROM todos WHERE termine=0 ORDER BY priorite DESC")
            elif filtre == "termines":
                # Récupère les tâches complétées
                cur.execute("SELECT * FROM todos WHERE termine=1")
            elif filtre in Todo.CATEGORIES:
                # Filtre par catégorie (paramétré pour sécurité)
                cur.execute("SELECT * FROM todos WHERE categorie=?", (filtre,))
            elif filtre in Todo.PRIORITES:
                # Filtre par priorité (paramétré pour sécurité)
                cur.execute("SELECT * FROM todos WHERE priorite=?", (filtre,))
            else:
                # Pas de filtre : retourne toutes les tâches, triées par statut puis priorité
                cur.execute("SELECT * FROM todos ORDER BY termine, priorite DESC")

            # Convertit chaque ligne SQL en objet Todo et retourne la liste
            return [Todo.from_dict(row) for row in cur.fetchall()]

    def trouver(self, todo_id):
        """
        Trouve un todo spécifique par son ID.
        
        Args :
            todo_id (int): ID de la tâche à rechercher
        
        Returns :
            Todo: Objet Todo si trouvé, None sinon
        """
        # Ouvre une connexion configurée pour retourner des dictionnaires
        with self._connexion() as conn:
            # Crée un curseur pour exécuter la requête
            cur = conn.cursor()
            # Récupère la tâche avec l'ID spécifié (requête paramétrée)
            cur.execute("SELECT * FROM todos WHERE id=?", (todo_id,))
            # Récupère une seule ligne (la première match)
            row = cur.fetchone()
            # Retourne un objet Todo ou None si rien n'a été trouvé
            return Todo.from_dict(row) if row else None

    def modifier(self, todo_id, **champs):
        """
        Modifie un ou plusieurs champs d'une tâche existante.
        
        Utilise des arguments nommés (**kwargs) pour spécifier les champs à mettre à jour.
        
        Args :
            todo_id (int): ID de la tâche à modifier
            **champs: Champs à modifier sous forme de clé=valeur
                      Ex: titre="Nouveau titre", priorite="haute"
        
        Returns :
            bool: True si la modification a réussi, False sinon
        
        Exemple :
            db.modifier(1, titre="Nouveau titre", termine=1)
        """
        # Vérifie qu'au moins un champ à modifier a été fourni
        if not champs:
            return False
        
        # Construit dynamiquement la clause SET de la requête SQL
        # Exemple : "titre=?, priorite=?" si 2 champs
        colonnes = ", ".join(f"{k}=?" for k in champs)
        # Prépare les valeurs à passer au placeholder (?)
        # Ajoute todo_id à la fin pour la clause WHERE
        valeurs  = list(champs.values()) + [todo_id]
        
        # Ouvre une connexion persistante
        with sqlite3.connect(self.fichier) as conn:
            # Crée un curseur pour exécuter la requête UPDATE
            cur = conn.cursor()
            # Exécute la requête UPDATE paramétrée
            cur.execute(f"UPDATE todos SET {colonnes} WHERE id=?", valeurs)
            # Valide les modifications (commit)
            conn.commit()
            # Retourne True si au moins une ligne a été affectée
            return cur.rowcount > 0

    def supprimer(self, todo_id):
        """
        Supprime une tâche de la base de données.
        
        Args :
            todo_id (int): ID de la tâche à supprimer
        
        Returns :
            bool: True si la suppression a réussi, False sinon
        """
        # Ouvre une connexion persistante
        with sqlite3.connect(self.fichier) as conn:
            # Crée un curseur pour exécuter la requête DELETE
            cur = conn.cursor()
            # Exécute la suppression paramétrée (protection contre injection SQL)
            cur.execute("DELETE FROM todos WHERE id=?", (todo_id,))
            # Valide la suppression (commit de la transaction)
            conn.commit()
            # Retourne True si au moins une ligne a été supprimée
            return cur.rowcount > 0

    def statistiques(self):
        """
        Calcule et retourne les statistiques globales des tâches.
        
        Returns :
            dict: Dictionnaire contenant :
                - "total" : nombre total de tâches
                - "termines" : nombre de tâches complétées
                - "actifs" : nombre de tâches en cours (total - termines)
        
        Exemple :
            {"total": 10, "termines": 3, "actifs": 7}
        """
        # Ouvre une connexion configurée pour retourner des dictionnaires
        with self._connexion() as conn:
            # Crée un curseur pour exécuter les requêtes d'agrégation
            cur = conn.cursor()
            
            # Compte le nombre total de tâches
            cur.execute("SELECT COUNT(*) as n FROM todos")
            total = cur.fetchone()["n"]
            
            # Compte le nombre de tâches terminées
            cur.execute("SELECT COUNT(*) as n FROM todos WHERE termine=1")
            termines = cur.fetchone()["n"]
            
            # Retourne un dictionnaire avec les statistiques
            # Les tâches actives sont calculées par différence
            return {"total": total, "termines": termines,
                    "actifs": total - termines}