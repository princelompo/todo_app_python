# ============================================
# cli.py — Interface ligne de commande
# ============================================

from manager import TodoManager
from todo import Todo


class CLI:
    """Interface utilisateur en ligne de commande"""

    def __init__(self):
        self.manager = TodoManager()
        self.commandes = {
            "1": ("Ajouter une tâche",    self.ajouter),
            "2": ("Lister les tâches",    self.lister),
            "3": ("Terminer une tâche",   self.terminer),
            "4": ("Modifier une tâche",   self.modifier),
            "5": ("Supprimer une tâche",  self.supprimer),
            "6": ("Statistiques",         self.statistiques),
            "0": ("Quitter",              self.quitter),
        }
        self.actif = True

    # ------------------------------------------
    # AFFICHAGE
    # ------------------------------------------

    def afficher_menu(self):
        print("\n" + "═" * 40)
        print("       📝 TODO APP — Menu principal")
        print("═" * 40)
        for cle, (label, _) in self.commandes.items():
            print(f"  {cle}. {label}")
        print("═" * 40)

    def afficher_todo(self, todo, detail=False):
        """Affiche un todo avec ou sans détails"""
        print(f"  {todo}")
        if detail and todo.description:
            print(f"     📄 {todo.description}")
        if detail:
            print(f"     📅 Créé le {todo.date_creation}")

    def afficher_todos(self, todos):
        """Affiche une liste de todos"""
        if not todos:
            print("  ℹ️  Aucune tâche trouvée")
            return
        print(f"\n  {'─'*36}")
        for todo in todos:
            self.afficher_todo(todo)
        print(f"  {'─'*36}")
        print(f"  Total : {len(todos)} tâche(s)")

    # ------------------------------------------
    # COMMANDES
    # ------------------------------------------

    def ajouter(self):
        print("\n  ── Ajouter une tâche ──")
        titre = input("  Titre       : ").strip()

        if not titre:
            print("  ❌ Le titre est obligatoire !")
            return

        description = input("  Description : ").strip()

        print(f"  Priorité    : {', '.join(Todo.PRIORITES)}")
        priorite = input("  Choix       : ").strip().lower()
        if priorite not in Todo.PRIORITES:
            priorite = "moyenne"

        print(f"  Catégorie   : {', '.join(Todo.CATEGORIES)}")
        categorie = input("  Choix       : ").strip().lower()
        if categorie not in Todo.CATEGORIES:
            categorie = "autre"

        try:
            todo = self.manager.ajouter(titre, description, priorite, categorie)
            print(f"\n  ✅ Tâche ajoutée :")
            self.afficher_todo(todo, detail=True)
        except ValueError as e:
            print(f"  ❌ {e}")

    def lister(self):
        print("\n  ── Lister les tâches ──")
        print("  Filtres : actifs | termines | travail | "
              "personnel | études | haute | moyenne | basse | (vide=tous)")
        filtre = input("  Filtre : ").strip().lower() or None

        todos = self.manager.lister(filtre)
        self.afficher_todos(todos)

    def terminer(self):
        print("\n  ── Terminer une tâche ──")
        self.afficher_todos(self.manager.lister("actifs"))

        try:
            todo_id = int(input("\n  ID de la tâche : "))
            todo    = self.manager.terminer(todo_id)
            print(f"  ✅ '{todo.titre}' marquée comme terminée !")
        except ValueError as e:
            print(f"  ❌ {e}")

    def modifier(self):
        print("\n  ── Modifier une tâche ──")
        self.afficher_todos(self.manager.lister())

        try:
            todo_id = int(input("\n  ID à modifier : "))
            todo    = self.manager.db.trouver(todo_id)
            if not todo:
                print(f"  ❌ Todo #{todo_id} introuvable !")
                return

            print(f"  Titre actuel : {todo.titre}")
            nouveau_titre = input("  Nouveau titre (vide=inchangé) : ").strip()

            print(f"  Priorité actuelle : {todo.priorite}")
            nouvelle_priorite = input("  Nouvelle priorité (vide=inchangée) : ").strip()

            champs = {}
            if nouveau_titre:
                champs["titre"] = nouveau_titre
            if nouvelle_priorite in Todo.PRIORITES:
                champs["priorite"] = nouvelle_priorite

            if champs:
                todo = self.manager.modifier(todo_id, **champs)
                print(f"  ✅ Tâche modifiée :")
                self.afficher_todo(todo, detail=True)
            else:
                print("  ℹ️  Aucune modification")

        except ValueError as e:
            print(f"  ❌ {e}")

    def supprimer(self):
        print("\n  ── Supprimer une tâche ──")
        self.afficher_todos(self.manager.lister())

        try:
            todo_id     = int(input("\n  ID à supprimer : "))
            confirmation = input(f"  Confirmer la suppression ? (o/n) : ")

            if confirmation.lower() == "o":
                todo = self.manager.supprimer(todo_id)
                print(f"  🗑️  '{todo.titre}' supprimée !")
            else:
                print("  ℹ️  Suppression annulée")

        except ValueError as e:
            print(f"  ❌ {e}")

    def statistiques(self):
        stats = self.manager.statistiques()
        todos = self.manager.lister()

        print("\n  ── Statistiques ──")
        print(f"  📊 Total    : {stats['total']} tâche(s)")
        print(f"  ✅ Terminées : {stats['termines']}")
        print(f"  ⬜ Actives  : {stats['actifs']}")

        if stats["total"] > 0:
            pct = (stats["termines"] / stats["total"]) * 100
            barre = "█" * int(pct / 5) + "░" * (20 - int(pct / 5))
            print(f"\n  Progression : [{barre}] {pct:.0f}%")

        # Répartition par catégorie
        categories = {}
        for todo in todos:
            categories[todo.categorie] = categories.get(todo.categorie, 0) + 1

        if categories:
            print("\n  Par catégorie :")
            for cat, nb in sorted(categories.items()):
                print(f"    {cat:<12} : {nb} tâche(s)")

    def quitter(self):
        print("\n  👋 À bientôt !")
        self.actif = False

    # ------------------------------------------
    # BOUCLE PRINCIPALE
    # ------------------------------------------

    def lancer(self):
        print("\n" + "═" * 40)
        print("   📝 Bienvenue dans votre Todo App !")
        print("═" * 40)

        while self.actif:
            self.afficher_menu()
            choix = input("  Votre choix : ").strip()

            if choix in self.commandes:
                _, action = self.commandes[choix]
                action()
            else:
                print("  ❌ Choix invalide, réessaie !")