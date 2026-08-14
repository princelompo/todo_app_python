# ============================================
# manager.py — Logique métier
# ============================================

from database import Database
from todo import Todo


class TodoManager:
    """Orchestre toutes les opérations sur les todos"""

    def __init__(self):
        self.db = Database()

    def ajouter(self, titre, description="",
                priorite="moyenne", categorie="autre"):
        """Crée et sauvegarde un nouveau todo"""
        if not titre.strip():
            raise ValueError("Le titre ne peut pas être vide !")

        todo    = Todo(titre, description, priorite, categorie)
        todo.id = self.db.ajouter(todo)
        return todo

    def terminer(self, todo_id):
        """Marque un todo comme terminé"""
        todo = self.db.trouver(todo_id)
        if not todo:
            raise ValueError(f"Todo #{todo_id} introuvable !")
        if todo.termine:
            raise ValueError(f"Todo #{todo_id} est déjà terminé !")
        self.db.modifier(todo_id, termine=1)
        return todo

    def rouvrir(self, todo_id):
        """Rouvre un todo terminé"""
        todo = self.db.trouver(todo_id)
        if not todo:
            raise ValueError(f"Todo #{todo_id} introuvable !")
        self.db.modifier(todo_id, termine=0)
        return todo

    def modifier(self, todo_id, **champs):
        """Modifie un todo existant"""
        todo = self.db.trouver(todo_id)
        if not todo:
            raise ValueError(f"Todo #{todo_id} introuvable !")
        self.db.modifier(todo_id, **champs)
        return self.db.trouver(todo_id)

    def supprimer(self, todo_id):
        """Supprime un todo"""
        todo = self.db.trouver(todo_id)
        if not todo:
            raise ValueError(f"Todo #{todo_id} introuvable !")
        self.db.supprimer(todo_id)
        return todo

    def lister(self, filtre=None):
        """Retourne la liste filtrée des todos"""
        return self.db.tous(filtre)

    def statistiques(self):
        """Retourne les statistiques"""
        return self.db.statistiques()