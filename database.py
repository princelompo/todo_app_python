# ============================================
# database.py — Gestion de la base de données
# ============================================

import sqlite3
from todo import Todo


class Database:
    """Gère toutes les opérations SQLite pour les todos"""

    def __init__(self, fichier="todos.db"):
        self.fichier = fichier
        self._initialiser()

    def _connexion(self):
        """Connexion avec résultats en dictionnaire"""
        conn = sqlite3.connect(self.fichier)
        conn.row_factory = lambda c, r: {
            col[0]: r[i] for i, col in enumerate(c.description)
        }
        return conn

    def _initialiser(self):
        """Crée la table si elle n'existe pas"""
        with sqlite3.connect(self.fichier) as conn:
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
            conn.commit()

    def ajouter(self, todo):
        """Insère un nouveau todo et retourne son id"""
        with sqlite3.connect(self.fichier) as conn:
            cur = conn.cursor()
            cur.execute("""
                INSERT INTO todos
                (titre, description, priorite, categorie, termine, date_creation)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                todo.titre, todo.description, todo.priorite,
                todo.categorie, int(todo.termine), todo.date_creation
            ))
            conn.commit()
            return cur.lastrowid

    def tous(self, filtre=None):
        """Retourne tous les todos, avec filtre optionnel"""
        with self._connexion() as conn:
            cur = conn.cursor()

            if filtre == "actifs":
                cur.execute("SELECT * FROM todos WHERE termine=0 ORDER BY priorite DESC")
            elif filtre == "termines":
                cur.execute("SELECT * FROM todos WHERE termine=1")
            elif filtre in Todo.CATEGORIES:
                cur.execute("SELECT * FROM todos WHERE categorie=?", (filtre,))
            elif filtre in Todo.PRIORITES:
                cur.execute("SELECT * FROM todos WHERE priorite=?", (filtre,))
            else:
                cur.execute("SELECT * FROM todos ORDER BY termine, priorite DESC")

            return [Todo.from_dict(row) for row in cur.fetchall()]

    def trouver(self, todo_id):
        """Trouve un todo par son id"""
        with self._connexion() as conn:
            cur = conn.cursor()
            cur.execute("SELECT * FROM todos WHERE id=?", (todo_id,))
            row = cur.fetchone()
            return Todo.from_dict(row) if row else None

    def modifier(self, todo_id, **champs):
        """Modifie les champs d'un todo"""
        if not champs:
            return False
        colonnes = ", ".join(f"{k}=?" for k in champs)
        valeurs  = list(champs.values()) + [todo_id]
        with sqlite3.connect(self.fichier) as conn:
            cur = conn.cursor()
            cur.execute(f"UPDATE todos SET {colonnes} WHERE id=?", valeurs)
            conn.commit()
            return cur.rowcount > 0

    def supprimer(self, todo_id):
        """Supprime un todo"""
        with sqlite3.connect(self.fichier) as conn:
            cur = conn.cursor()
            cur.execute("DELETE FROM todos WHERE id=?", (todo_id,))
            conn.commit()
            return cur.rowcount > 0

    def statistiques(self):
        """Retourne les statistiques globales"""
        with self._connexion() as conn:
            cur = conn.cursor()
            cur.execute("SELECT COUNT(*) as n FROM todos")
            total = cur.fetchone()["n"]
            cur.execute("SELECT COUNT(*) as n FROM todos WHERE termine=1")
            termines = cur.fetchone()["n"]
            return {"total": total, "termines": termines,
                    "actifs": total - termines}