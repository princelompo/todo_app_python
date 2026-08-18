# ============================================
# cli.py — Interface ligne de commande
# ============================================
#
# Ce module fournit l'interface utilisateur en ligne de commande (CLI).
# Il gère l'affichage du menu, l'interaction avec l'utilisateur,
# et l'affichage des résultats des opérations.
#
# Responsabilités :
#   - Afficher le menu principal
#   - Recueillir les saisies utilisateur
#   - Appeler les méthodes du TodoManager
#   - Afficher les tâches et résultats de manière lisible
#   - Gérer les erreurs et afficher les messages utilisateur
#
# Architecture :
#   CLI (interface utilisateur)
#     ↓
#   TodoManager (logique métier)
#     ↓
#   Database (accès aux données)
#
# ============================================

from manager import TodoManager
from todo import Todo


class CLI:
    """
    Interface utilisateur en ligne de commande.
    
    Gère l'interaction avec l'utilisateur et l'affichage des résultats.
    Utilise TodoManager pour exécuter les opérations métier.
    
    Attributs :
        manager (TodoManager): Gestionnaire de tâches
        commandes (dict): Dictionnaire des commandes disponibles
        actif (bool): Indicateur d'état de la boucle principale
    """

    def __init__(self):
        """
        Initialise l'interface CLI.
        
        Crée une instance de TodoManager et configure les commandes disponibles.
        """
        # Crée le gestionnaire de tâches
        self.manager = TodoManager()
        # Dictionnaire mappant les touches aux labels et méthodes de traitement
        # Format: "touche": ("Label pour affichage", fonction_a_appeler)
        self.commandes = {
            "1": ("Ajouter une tâche",    self.ajouter),
            "2": ("Lister les tâches",    self.lister),
            "3": ("Terminer une tâche",   self.terminer),
            "4": ("Modifier une tâche",   self.modifier),
            "5": ("Supprimer une tâche",  self.supprimer),
            "6": ("Statistiques",         self.statistiques),
            "0": ("Quitter",              self.quitter),
        }
        # Indicateur pour contrôler la boucle principale
        self.actif = True

    # ==================================================
    # AFFICHAGE — Méthodes de présentation des données
    # ==================================================

    def afficher_menu(self):
        """
        Affiche le menu principal avec les options disponibles.
        
        Affiche un menu formaté avec des séparateurs visuels et
        toutes les commandes numérotées.
        """
        # Affiche le titre du menu avec séparateurs
        print("\n" + "═" * 40)
        print("       📝 TODO APP — Menu principal")
        print("═" * 40)
        # Affiche chaque commande disponible
        for cle, (label, _) in self.commandes.items():
            print(f"  {cle}. {label}")
        # Affiche un séparateur de fermeture
        print("═" * 40)

    def afficher_todo(self, todo, detail=False):
        """
        Affiche une tâche individuelle avec ou sans détails.
        
        Args :
            todo (Todo): La tâche à afficher
            detail (bool): Si True, affiche description et date (défaut: False)
        """
        # Affiche le todo via sa méthode __str__ (formaté avec emoji)
        print(f"  {todo}")
        # Affiche la description si détails demandés et description existe
        if detail and todo.description:
            print(f"     📄 {todo.description}")
        # Affiche la date de création si détails demandés
        if detail:
            print(f"     📅 Créé le {todo.date_creation}")

    def afficher_todos(self, todos):
        """
        Affiche une liste de tâches avec formatage et résumé.
        
        Args :
            todos (list): Liste de tâches (objets Todo) à afficher
        """
        # Gère le cas où la liste est vide
        if not todos:
            print("  ℹ️  Aucune tâche trouvée")
            return
        # Affiche un séparateur de début
        print(f"\n  {'─'*36}")
        # Affiche chaque tâche de la liste
        for todo in todos:
            self.afficher_todo(todo)
        # Affiche un séparateur de fin
        print(f"  {'─'*36}")
        # Affiche le nombre total de tâches
        print(f"  Total : {len(todos)} tâche(s)")

    # ==================================================
    # COMMANDES — Implémentations des opérations utilisateur
    # ==================================================

    def ajouter(self):
        """
        Commande : Ajouter une nouvelle tâche.
        
        Recueille les informations (titre, description, priorité, catégorie)
        et crée une nouvelle tâche via le manager.
        Gère les erreurs et affiche un message de confirmation.
        """
        # Affiche le titre de la commande
        print("\n  ── Ajouter une tâche ──")
        # Demande le titre de la tâche
        titre = input("  Titre       : ").strip()

        # Valide que le titre n'est pas vide
        if not titre:
            print("  ❌ Le titre est obligatoire !")
            return

        # Demande la description (optionnelle)
        description = input("  Description : ").strip()

        # Affiche les priorités disponibles et demande la sélection
        print(f"  Priorité    : {', '.join(Todo.PRIORITES)}")
        priorite = input("  Choix       : ").strip().lower()
        # Applique une valeur par défaut si la sélection est invalide
        if priorite not in Todo.PRIORITES:
            priorite = "moyenne"

        # Affiche les catégories disponibles et demande la sélection
        print(f"  Catégorie   : {', '.join(Todo.CATEGORIES)}")
        categorie = input("  Choix       : ").strip().lower()
        # Applique une valeur par défaut si la sélection est invalide
        if categorie not in Todo.CATEGORIES:
            categorie = "autre"

        # Essaie de créer la tâche via le manager
        try:
            todo = self.manager.ajouter(titre, description, priorite, categorie)
            # Affiche un message de succès avec détails de la tâche
            print(f"\n  ✅ Tâche ajoutée :")
            self.afficher_todo(todo, detail=True)
        except ValueError as e:
            # Affiche le message d'erreur
            print(f"  ❌ {e}")

    def lister(self):
        """
        Commande : Lister les tâches avec filtre optionnel.
        
        Affiche les tâches filtrées selon le critère spécifié par l'utilisateur.
        Supports filtres : actifs, termines, catégories, priorités.
        """
        # Affiche le titre de la commande
        print("\n  ── Lister les tâches ──")
        # Affiche les filtres disponibles
        print("  Filtres : actifs | termines | travail | "
              "personnel | études | haute | moyenne | basse | (vide=tous)")
        # Recueille le filtre auprès de l'utilisateur (None si vide)
        filtre = input("  Filtre : ").strip().lower() or None

        # Récupère les tâches filtrées du manager
        todos = self.manager.lister(filtre)
        # Affiche la liste de tâches avec formatting
        self.afficher_todos(todos)

    def terminer(self):
        """
        Commande : Marquer une tâche comme terminée.
        
        Affiche les tâches actives et demande l'ID de celle à terminer.
        Gère les erreurs (ID invalide, tâche introuvable, etc.).
        """
        # Affiche le titre de la commande
        print("\n  ── Terminer une tâche ──")
        # Affiche toutes les tâches actives (non terminées)
        self.afficher_todos(self.manager.lister("actifs"))

        # Essaie de terminer la tâche sélectionnée
        try:
            # Demande l'ID de la tâche et convertit en entier
            todo_id = int(input("\n  ID de la tâche : "))
            # Marque la tâche comme terminée via le manager
            todo    = self.manager.terminer(todo_id)
            # Affiche un message de succès
            print(f"  ✅ '{todo.titre}' marquée comme terminée !")
        except ValueError as e:
            # Gère les erreurs de conversion d'entier et erreurs métier
            print(f"  ❌ {e}")

    def modifier(self):
        """
        Commande : Modifier une tâche existante.
        
        Affiche les tâches, demande l'ID, et permet de modifier le titre
        et la priorité. Les champs vides sont ignorés (non modifiés).
        """
        # Affiche le titre de la commande
        print("\n  ── Modifier une tâche ──")
        # Affiche toutes les tâches
        self.afficher_todos(self.manager.lister())

        # Essaie de modifier la tâche sélectionnée
        try:
            # Demande l'ID et convertit en entier
            todo_id = int(input("\n  ID à modifier : "))
            # Récupère la tâche actuelle pour afficher ses valeurs
            todo    = self.manager.db.trouver(todo_id)
            # Vérifie que la tâche existe
            if not todo:
                print(f"  ❌ Todo #{todo_id} introuvable !")
                return

            # Affiche le titre actuel et demande la modification
            print(f"  Titre actuel : {todo.titre}")
            nouveau_titre = input("  Nouveau titre (vide=inchangé) : ").strip()

            # Affiche la priorité actuelle et demande la modification
            print(f"  Priorité actuelle : {todo.priorite}")
            nouvelle_priorite = input("  Nouvelle priorité (vide=inchangée) : ").strip()

            # Collecte uniquement les champs modifiés dans un dictionnaire
            champs = {}
            if nouveau_titre:
                champs["titre"] = nouveau_titre
            if nouvelle_priorite in Todo.PRIORITES:
                champs["priorite"] = nouvelle_priorite

            # Valide et affiche les modifications
            if champs:
                # Applique les modifications via le manager
                todo = self.manager.modifier(todo_id, **champs)
                # Affiche la tâche modifiée
                print(f"  ✅ Tâche modifiée :")
                self.afficher_todo(todo, detail=True)
            else:
                # Aucun champ valide n'a été fourni
                print("  ℹ️  Aucune modification")

        except ValueError as e:
            # Gère les erreurs de conversion d'entier et erreurs métier
            print(f"  ❌ {e}")

    def supprimer(self):
        """
        Commande : Supprimer définitivement une tâche.
        
        Affiche les tâches, demande l'ID, et requiert une confirmation
        avant la suppression définitive.
        """
        # Affiche le titre de la commande
        print("\n  ── Supprimer une tâche ──")
        # Affiche toutes les tâches
        self.afficher_todos(self.manager.lister())

        # Essaie de supprimer la tâche sélectionnée
        try:
            # Demande l'ID et convertit en entier
            todo_id     = int(input("\n  ID à supprimer : "))
            # Demande une confirmation avant suppression
            confirmation = input(f"  Confirmer la suppression ? (o/n) : ")

            # Exécute la suppression seulement si confirmée
            if confirmation.lower() == "o":
                # Supprime la tâche via le manager
                todo = self.manager.supprimer(todo_id)
                # Affiche un message de confirmation
                print(f"  🗑️  '{todo.titre}' supprimée !")
            else:
                # L'utilisateur a annulé
                print("  ℹ️  Suppression annulée")

        except ValueError as e:
            # Gère les erreurs de conversion d'entier et erreurs métier
            print(f"  ❌ {e}")

    def statistiques(self):
        """
        Commande : Afficher les statistiques globales des tâches.
        
        Affiche :
          - Total de tâches
          - Nombre de tâches terminées et actives
          - Barre de progression visuelle
          - Répartition par catégorie
        """
        # Récupère les statistiques globales du manager
        stats = self.manager.statistiques()
        # Récupère toutes les tâches pour l'analyse par catégorie
        todos = self.manager.lister()

        # Affiche le titre de la section
        print("\n  ── Statistiques ──")
        # Affiche les statistiques principales
        print(f"  📊 Total    : {stats['total']} tâche(s)")
        print(f"  ✅ Terminées : {stats['termines']}")
        print(f"  ⬜ Actives  : {stats['actifs']}")

        # Affiche une barre de progression visuelle si des tâches existent
        if stats["total"] > 0:
            # Calcule le pourcentage d'achèvement
            pct = (stats["termines"] / stats["total"]) * 100
            # Crée une barre de progression avec caractères visuels
            # 20 caractères total, 5% par caractère
            barre = "█" * int(pct / 5) + "░" * (20 - int(pct / 5))
            # Affiche la barre et le pourcentage
            print(f"\n  Progression : [{barre}] {pct:.0f}%")

        # Analyse la répartition des tâches par catégorie
        categories = {}
        for todo in todos:
            # Compte les tâches par catégorie
            categories[todo.categorie] = categories.get(todo.categorie, 0) + 1

        # Affiche la répartition par catégorie si des tâches existent
        if categories:
            print("\n  Par catégorie :")
            # Affiche chaque catégorie et son nombre de tâches
            for cat, nb in sorted(categories.items()):
                print(f"    {cat:<12} : {nb} tâche(s)")

    def quitter(self):
        """
        Commande : Quitter l'application.
        
        Affiche un message d'au revoir et arrête la boucle principale.
        """
        # Affiche un message de départ
        print("\n  👋 À bientôt !")
        # Arrête la boucle principale en mettant actif à False
        self.actif = False

    # ==================================================
    # BOUCLE PRINCIPALE — Orchestration de l'application
    # ==================================================

    def lancer(self):
        """
        Lance la boucle principale de l'application.
        
        Affiche le message de bienvenue, puis exécute une boucle infinie
        qui :
          1. Affiche le menu
          2. Recueille le choix de l'utilisateur
          3. Exécute la commande correspondante
          4. Répète jusqu'à ce que l'utilisateur quitte (choix 0)
        """
        # Affiche le message de bienvenue
        print("\n" + "═" * 40)
        print("   📝 Bienvenue dans votre Todo App !")
        print("═" * 40)

        # Boucle principale de l'application
        while self.actif:
            # Affiche le menu et les options disponibles
            self.afficher_menu()
            # Recueille le choix de l'utilisateur
            choix = input("  Votre choix : ").strip()

            # Vérifie que le choix existe dans le dictionnaire des commandes
            if choix in self.commandes:
                # Récupère la fonction associée au choix (deuxième élément du tuple)
                _, action = self.commandes[choix]
                # Exécute la fonction de commande
                action()
            # Si le choix n'existe pas, la boucle recommence simplement
            else:
                print("  ❌ Choix invalide, réessaie !")