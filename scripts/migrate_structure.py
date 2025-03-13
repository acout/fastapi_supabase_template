#!/usr/bin/env python
"""
Script pour migrer de l'ancienne structure du projet vers la nouvelle.

Ce script va :
1. Comparer les dossiers /app et /backend/app
2. Copier les fichiers manquants de /app vers /backend/app
3. Créer un rapport de migration

Utilisation :
    python scripts/migrate_structure.py
"""

import os
import shutil
import sys
from pathlib import Path

# Chemins principaux
ROOT_DIR = Path(os.getcwd())
SRC_DIR = ROOT_DIR / "app"
DST_DIR = ROOT_DIR / "backend" / "app"

# Vérification des dossiers
def check_directories():
    """Vérifie si les dossiers source et destination existent."""
    if not SRC_DIR.exists():
        print(f"Erreur: Le dossier source {SRC_DIR} n'existe pas.")
        return False
    if not DST_DIR.exists():
        print(f"Création du dossier de destination {DST_DIR}")
        DST_DIR.mkdir(parents=True, exist_ok=True)
    return True

# Liste des fichiers/dossiers à copier
def list_files_to_copy():
    """Liste les fichiers qui doivent être copiés de /app vers /backend/app."""
    files_to_copy = []
    
    for src_path in SRC_DIR.glob("**/*"):
        # Chemin relatif par rapport à SRC_DIR
        rel_path = src_path.relative_to(SRC_DIR)
        dst_path = DST_DIR / rel_path
        
        # Si c'est un répertoire et qu'il n'existe pas, il faut le créer
        if src_path.is_dir() and not dst_path.exists():
            files_to_copy.append((src_path, dst_path, "directory"))
        
        # Si c'est un fichier
        elif src_path.is_file():
            # S'il n'existe pas dans la destination
            if not dst_path.exists():
                files_to_copy.append((src_path, dst_path, "new_file"))
            # S'il existe mais a un contenu différent
            elif src_path.read_bytes() != dst_path.read_bytes():
                files_to_copy.append((src_path, dst_path, "modified_file"))
    
    return files_to_copy

# Copie les fichiers
def copy_files(files_to_copy):
    """Copie les fichiers de la liste dans la destination."""
    for src_path, dst_path, file_type in files_to_copy:
        if file_type == "directory":
            print(f"Création du répertoire: {dst_path}")
            dst_path.mkdir(parents=True, exist_ok=True)
        else:
            print(f"Copie du fichier: {src_path} -> {dst_path}")
            # Assure-toi que le répertoire parent existe
            dst_path.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src_path, dst_path)

# Génère un rapport
def generate_report(files_to_copy):
    """Génère un rapport de migration."""
    if not files_to_copy:
        print("\nRapport de migration:")
        print("Aucun fichier n'a été copié. La structure est déjà à jour.")
        return
    
    print("\nRapport de migration:")
    print(f"Nombre total d'éléments copiés: {len(files_to_copy)}")
    
    directories = [f for f in files_to_copy if f[2] == "directory"]
    new_files = [f for f in files_to_copy if f[2] == "new_file"]
    modified_files = [f for f in files_to_copy if f[2] == "modified_file"]
    
    print(f"Répertoires créés: {len(directories)}")
    print(f"Nouveaux fichiers: {len(new_files)}")
    print(f"Fichiers modifiés: {len(modified_files)}")
    
    # Liste les modifications en détail
    if directories:
        print("\nRépertoires créés:")
        for src, dst, _ in directories:
            print(f"- {dst}")
    
    if new_files:
        print("\nNouveaux fichiers:")
        for src, dst, _ in new_files:
            print(f"- {dst}")
    
    if modified_files:
        print("\nFichiers modifiés:")
        for src, dst, _ in modified_files:
            print(f"- {dst}")

def main():
    print("Début de la migration de structure du projet...")
    
    if not check_directories():
        sys.exit(1)
    
    files_to_copy = list_files_to_copy()
    
    if files_to_copy:
        choice = input(f"\n{len(files_to_copy)} éléments à copier. Voulez-vous continuer? (y/n): ")
        if choice.lower() != 'y':
            print("Migration annulée.")
            sys.exit(0)
        
        copy_files(files_to_copy)
    
    generate_report(files_to_copy)
    
    print("\nMigration terminée.")
    print("Important: Vérifiez manuellement les fichiers copiés pour vous assurer de leur intégrité.")
    print("Une fois que vous êtes sûr que la migration est correcte, vous pouvez supprimer le dossier /app.")

if __name__ == "__main__":
    main()
