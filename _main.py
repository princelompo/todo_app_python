# ============================================
# _main.py — Point d'entrée de l'application
# ============================================
# 
# Ce module constitue le point d'entrée principal de l'application Todo.
# Il crée une instance de la classe CLI et lance la boucle principale.
# 
# Architecture :
#   _main.py (point d'entrée)
#     ↓
#   cli.py (interface utilisateur)
#     ↓
#   manager.py (logique métier)
#     ↓
#   database.py (accès aux données)
#     ↓
#   todo.py (modèle de données)
#
# ============================================

from cli import CLI

if __name__ == "__main__":
    """Bloc d'exécution principal"""
    # Crée une instance de la classe CLI (interface ligne de commande)
    app = CLI()
    # Lance la boucle principale de l'application
    app.lancer()