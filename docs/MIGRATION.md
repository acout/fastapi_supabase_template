# Guide de migration vers la nouvelle structure

## Aperçu

Ce document explique les changements apportés à la structure du projet FastAPI Supabase Template et comment migrer un projet existant vers cette nouvelle structure.

## Pourquoi cette refonte ?

Le projet présentait plusieurs incohérences structurelles résultant du fork du template original :

- Structure d'application dupliquée (/app et /backend/app)
- Fichiers de configuration multiples (pyproject.toml à la racine et dans /backend)
- Problèmes potentiels de démarrage dans Docker (chemins incohérents)
- Support Supabase local non nécessaire mais présent
- Scripts et outils dupliqués entre la racine et le dossier backend

Ces incohérences rendaient le projet difficile à maintenir et à comprendre pour les nouveaux développeurs.

## Changements majeurs

1. **Simplification de la structure** : Tout le code est maintenant dans `/backend`
2. **Suppression du support Supabase local intégré** : Utilisation de la CLI Supabase directement si nécessaire
3. **Unification des configurations** : Un seul fichier pyproject.toml dans `/backend`
4. **Amélioration des tests** : Support pour les tests avec et sans dépendances externes
5. **Simplification du Dockerfile** : Pointe vers la nouvelle structure

## Nouvelle structure

```
/
|-- .github/           # GitHub Actions et configurations
|-- backend/           # Tout le code du projet
|   |-- alembic/       # Migrations de base de données
|   |-- app/           # Code source principal
|   |   |-- api/       # Endpoints API
|   |   |-- core/      # Configurations et utilitaires principaux
|   |   |-- crud/      # Opérations CRUD
|   |   |-- models/    # Modèles de données
|   |   |-- schemas/   # Schémas Pydantic
|   |   |-- services/  # Services métier
|   |   |-- utils/     # Utilitaires génériques
|   |   |-- main.py    # Point d'entrée de l'application
|   |-- scripts/       # Scripts utilitaires
|   |-- tests/         # Tests
|   |-- .env           # Environnement de développement
|   |-- .env.test      # Environnement de test
|   |-- pyproject.toml # Configuration du projet
|-- .pre-commit-config.yaml   # Hooks pre-commit
|-- Dockerfile         # Configuration Docker
|-- docker-compose.yml # Configuration docker-compose
```

## Migration d'un projet existant

Nous fournissons un script de migration pour faciliter la transition :

```bash
python scripts/migrate_structure.py
```

Ce script :
1. Compare les dossiers `/app` et `/backend/app`
2. Copie les fichiers manquants de `/app` vers `/backend/app`
3. Crée un rapport de migration

### Étapes de migration manuelle

Si vous préférez effectuer la migration manuellement, voici les étapes à suivre :

1. **Vérifier les fichiers dans `/app`** :
   ```bash
   find app -type f | sort
   ```

2. **Vérifier les fichiers dans `/backend/app`** :
   ```bash
   find backend/app -type f | sort
   ```

3. **Copier les fichiers manquants** de `/app` vers `/backend/app`

4. **Supprimer le dossier `/app`** une fois la migration validée

5. **Modifier les chemins d'importation** dans vos fichiers si nécessaire

6. **Mettre à jour les scripts** qui référencent l'ancien chemin

## Tests sans dépendances externes

La nouvelle structure facilite les tests sans dépendances externes grâce à trois variables d'environnement :

- `MOCK_SUPABASE=true` : Utilise un client Supabase simulé au lieu d'une connexion réelle
- `SKIP_DB_CHECK=true` : Ignore les vérifications de connexion à la base de données
- `SKIP_ENV_CHECK=true` : Ignore les vérifications des variables d'environnement

Vous pouvez utiliser les scripts fournis :

```bash
# Tests avec mocks (sans dépendances externes)
bash backend/scripts/test-with-mocks.sh

# Tests avec connexion réelle à Supabase
bash backend/scripts/test-with-supabase.sh
```

## Docker et déploiement

Le `Dockerfile` et `docker-compose.yml` ont été mis à jour pour refléter la nouvelle structure :

- Le point d'entrée est maintenant `uvicorn app.main:app`
- Le contexte de construction est maintenant le répertoire racine
- Le volume monté est maintenant `/backend`

Pour construire et lancer l'application :

```bash
docker-compose up --build
```

## Questions fréquentes

### Pourquoi avoir supprimé le support Supabase local intégré ?

Le support Supabase local est maintenant géré via la CLI Supabase directement, sans passer par Docker Compose. Cela simplifie la configuration et évite les problèmes potentiels.

Pour utiliser Supabase en local :

```bash
# À la racine du projet
supabase start
```

### Comment exécuter les tests sans Supabase ?

Utilisez les variables d'environnement ou le script fourni :

```bash
MOCK_SUPABASE=true SKIP_DB_CHECK=true pytest backend/tests/
```

Ou

```bash
bash backend/scripts/test-with-mocks.sh
```

### Comment migrer mes GitHub Actions ?

Mettez à jour vos workflows GitHub Actions pour refléter la nouvelle structure :

- Changez les chemins des tests de `/app` à `/backend/app`
- Utilisez les variables d'environnement pour les tests sans dépendances externes

Exemple :

```yaml
- name: Run tests with mocks
  run: |
    cd backend
    MOCK_SUPABASE=true SKIP_DB_CHECK=true pytest tests/
```
