# Scripts utilitaires

Ce dossier contient les scripts utilitaires pour le développement, les tests et le déploiement.

## Scripts de test

### test-with-mocks.sh

Exécute les tests en utilisant des mocks pour Supabase et en ignorant les vérifications de connexion à la base de données.

```bash
bash scripts/test-with-mocks.sh
```

Options supplémentaires :

```bash
# Exécuter un fichier de test spécifique
bash scripts/test-with-mocks.sh tests/api/test_auth.py

# Exécuter avec génération de couverture
bash scripts/test-with-mocks.sh --cov=app
```

### test-with-supabase.sh

Exécute les tests en utilisant une connexion réelle à Supabase.

```bash
bash scripts/test-with-supabase.sh
```

## Variables d'environnement de test

Les tests peuvent être configurés avec les variables d'environnement suivantes :

- `MOCK_SUPABASE=true|false` : Utilise un client Supabase simulé au lieu d'une connexion réelle
- `SKIP_DB_CHECK=true|false` : Ignore les vérifications de connexion à la base de données
- `SKIP_ENV_CHECK=true|false` : Ignore les vérifications des variables d'environnement

## Utilisation dans les tests

Dans vos tests, vous pouvez utiliser les fonctions du module `app.utils.testing` :

```python
from app.utils.testing import should_skip_db_check, get_supabase_client

def test_something():
    # Vérifier si on doit ignorer les vérifications de BDD
    if should_skip_db_check():
        # Utiliser un mock ou une alternative
        ...
    else:
        # Utiliser la vraie BDD
        ...
    
    # Obtenir un client Supabase (réel ou mock selon l'environnement)
    client = get_supabase_client()
    # Utiliser le client
    ...
```
