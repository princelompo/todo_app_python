from datetime import datetime

print("BIENVENUE DANS L'APPLICATION DE GESTION DE TÂCHES !...")

class Todo:
    def __init__(self, id, titre, description="", priorite="moyenne", categorie="autre", termine=False, date_creation=None):
        self.id = id
        self.titre = titre
        self.description = description
        self.priorite = priorite
        self.categorie = categorie
        self.termine = termine
        self.date_creation = date_creation or datetime.now().strftime("%d/%m/%Y %H:%M")

    def __str__(self):
        return f"Todo #{self.id} - {self.titre} (Priorité: {self.priorite}, Catégorie: {self.categorie}, Terminé: {'✅' if self.termine else '❌'}) - Créé le {self.date_creation}"

class Database:
    def __init__(self):
        self.todos = []
        self.next_id = 1

    def ajouter(self, todo):
        todo.id = self.next_id
        self.todos.append(todo)
        self.next_id += 1
        return todo.id

    def trouver(self, todo_id):
        for todo in self.todos:
            if todo.id == todo_id:
                return todo
        return None

    def modifier(self, todo_id, **kwargs):
        todo = self.trouver(todo_id)
        if not todo:
            return False
        for key, value in kwargs.items():
            setattr(todo, key, value)
        return True

class Manager:
    def __init__(self):
        self.db = Database()

    def ajouter(self, titre, description="", priorite="moyenne", categorie="autre"):
        if not titre.strip():
            raise ValueError("Le titre ne peut pas être vide !")
        todo = Todo(id=None, titre=titre, description=description, priorite=priorite, categorie=categorie)
        todo.id = self.db.ajouter(todo)
        return todo

    def terminer(self, todo_id):
        todo = self.db.trouver(todo_id)
        if not todo:
            raise ValueError(f"Todo #{todo_id} introuvable !")
        if todo.termine:
            raise ValueError(f"Todo #{todo_id} est déjà terminé !")
        self.db.modifier(todo_id, termine=True)
        return todo

    def lister(self):
        return self.db.todos

    def supprimer(self, todo_id):
        todo = self.db.trouver(todo_id)
        if not todo:
            raise ValueError(f"Todo #{todo_id} introuvable !")
        self.db.todos.remove(todo)
        return todo

    def modifier(self, todo_id, **kwargs):
        todo = self.db.trouver(todo_id)
        if not todo:
            raise ValueError(f"Todo #{todo_id} introuvable !")
        self.db.modifier(todo_id, **kwargs)
        return todo

    def rouvrir(self, todo_id):
        todo = self.db.trouver(todo_id)
        if not todo:
            raise ValueError(f"Todo #{todo_id} introuvable !")
        self.db.modifier(todo_id, termine=False)
        return todo

class CLI:
    def __init__(self):
        self.manager = Manager()
        self.actions = {
            "1": self.ajouter_tache,
            "2": self.lister_taches,
            "3": self.terminer_tache,
            "4": self.supprimer_tache,
            "5": self.modifier_tache,
            "6": self.rouvrir_tache,
            "0": self.quitter
        }

    def lancer(self):
        while True:
            print("\n=== MENU PRINCIPAL ===")
            print("1. Ajouter une tâche")
            print("2. Lister les tâches")
            print("3. Terminer une tâche")
            print("4. Supprimer une tâche")
            print("5. Modifier une tâche")
            print("6. Rouvrir une tâche")
            print("0. Quitter")
            choix = input("Choisissez une option: ")
            action = self.actions.get(choix)
            if action:
                action()
            else:
                print("  ❌ Choix invalide, réessaie !")

    def ajouter_tache(self):
        titre = input("Titre de la tache: ").strip()
        description = input("Description (optionnelle): ").strip()
        priorite = input("Priorité (basse/moyenne/haute): ").strip().lower()
        categorie = input("Catégorie (travail/personnel/études/autre): ").strip().lower()
        try:
            todo = self.manager.ajouter(titre, description, priorite, categorie)
            print(f"✅ Tâche ajoutée: {todo}")
        except ValueError as e:
            print(f"❌ Erreur: {e}")

    def lister_taches(self):
        todos = self.manager.lister()
        if not todos:
            print("Aucune tâche trouvée.")
            return
        for todo in todos:
            print(todo)

    def terminer_tache(self):
        try:
            todo_id = int(input("ID de la tâche à terminer: "))
            todo = self.manager.terminer(todo_id)
            print(f"✅ Tâche terminée: {todo}")
        except ValueError as e:
            print(f"❌ Erreur: {e}")

    def supprimer_tache(self):
        try:
            todo_id = int(input("ID de la tâche à supprimer: "))
            todo = self.manager.supprimer(todo_id)
            print(f"✅ Tâche supprimée: {todo}")
        except ValueError as e:
            print(f"❌ Erreur: {e}")

    def modifier_tache(self):
        try:
            todo_id = int(input("ID de la tâche à modifier: "))
            titre = input("Nouveau titre (laisser vide pour ne pas changer): ").strip()
            description = input("Nouvelle description (laisser vide pour ne pas changer): ").strip()
            priorite = input("Nouvelle priorité (basse/moyenne/haute, laisser vide pour ne pas changer): ").strip().lower()
            categorie = input("Nouvelle catégorie (travail/personnel/études/autre, laisser vide pour ne pas changer): ").strip().lower()
            kwargs = {}
            if titre:
                kwargs['titre'] = titre
            if description:
                kwargs['description'] = description
            if priorite:
                kwargs['priorite'] = priorite
            if categorie:
                kwargs['categorie'] = categorie
            todo = self.manager.modifier(todo_id, **kwargs)
            print(f"✅ Tâche modifiée: {todo}")
        except ValueError as e:
            print(f"❌ Erreur: {e}")

    def rouvrir_tache(self):
        try:
            todo_id = int(input("ID de la tâche à rouvrir: "))
            todo = self.manager.rouvrir(todo_id)
            print(f"✅ Tâche rouverte: {todo}")
        except ValueError as e:
            print(f"❌ Erreur: {e}")

    def quitter(self):
        print("Au revoir ! 👋")
        exit(0)


if __name__ == "__main__":
    app = CLI()
    app.lancer()