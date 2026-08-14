# ============================================
# todo.py — Classe Todo (modèle de données)
# ============================================

from datetime import datetime


class Todo:
    """Représente une tâche dans l'application"""

    # Priorités possibles
    PRIORITES = ["basse", "moyenne", "haute"]

    # Catégories possibles
    CATEGORIES = ["travail", "personnel", "études", "autre"]

    def __init__(self, titre, description="", priorite="moyenne",
                 categorie="autre", id=None, termine=False,
                 date_creation=None):

        self.id           = id
        self.titre        = titre
        self.description  = description
        self.priorite     = priorite if priorite in self.PRIORITES else "moyenne"
        self.categorie    = categorie if categorie in self.CATEGORIES else "autre"
        self.termine      = termine
        self.date_creation = date_creation or datetime.now().strftime("%d/%m/%Y %H:%M")

    def to_dict(self):
        """Convertit l'objet en dictionnaire"""
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
        """Crée un Todo depuis un dictionnaire"""
        return cls(
            id           = data.get("id"),
            titre        = data["titre"],
            description  = data.get("description", ""),
            priorite     = data.get("priorite", "moyenne"),
            categorie    = data.get("categorie", "autre"),
            termine      = bool(data.get("termine", False)),
            date_creation= data.get("date_creation")
        )

    def __str__(self):
        statut   = "✅" if self.termine else "⬜"
        priorite = {"basse": "🟢", "moyenne": "🟡", "haute": "🔴"}
        return (f"{statut} [{self.id}] {self.titre} "
                f"{priorite.get(self.priorite, '')} "
                f"({self.categorie})")