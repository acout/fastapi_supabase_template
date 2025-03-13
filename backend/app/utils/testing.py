# Utilitaires pour les tests avec ou sans dépendances externes.
import os
from unittest.mock import MagicMock


class MockSupabaseClient:
    """Mock pour le client Supabase utilisé dans les tests."""
    
    def __init__(self):
        # Simuler les tables principales avec des opérations mock
        self.table = MagicMock()
        self.table.select.return_value = self.table
        self.table.eq.return_value = self.table
        self.table.execute.return_value = {"data": [], "error": None}
        
        # Simulation de l'authentification
        self.auth = MagicMock()
        self.auth.sign_in.return_value = {"user": {"id": "mock-user-id"}, "session": {"access_token": "mock-token"}}
        
        # Simulation des fonctions stockées
        self.functions = MagicMock()
        self.functions.invoke.return_value = {"data": {}, "error": None}
        
        # Simulation du stockage
        self.storage = MagicMock()
        self.storage.from_.return_value = self.storage
        self.storage.upload.return_value = {"Key": "mock-file-path"}
        self.storage.create_signed_url.return_value = {"signedURL": "https://mock-signed-url.com"}
        self.storage.list.return_value = {"data": [{"name": "mock-file.txt"}], "error": None}
    
    def table(self, table_name):
        """Simuler l'accès à une table."""
        self.table.table_name = table_name
        return self.table
    
    def from_(self, bucket_name):
        """Simuler l'accès à un bucket de stockage."""
        self.storage.bucket_name = bucket_name
        return self.storage


def get_supabase_client():
    """
    Fournit un client Supabase réel ou simulé selon l'environnement.
    
    Returns:
        Un client Supabase réel ou un MockSupabaseClient.
    """
    if os.environ.get("MOCK_SUPABASE") == "true":
        return MockSupabaseClient()
    
    # Importer dynamiquement pour éviter les dépendances circulaires
    from app.core.config import get_settings
    from supabase import create_client
    
    settings = get_settings()
    # Création du client Supabase réel
    return create_client(settings.SUPABASE_URL, settings.SUPABASE_KEY)


def should_skip_db_check():
    """
    Vérifie si les tests devraient ignorer les vérifications de base de données.
    
    Returns:
        bool: True si les vérifications de BDD doivent être ignorées.
    """
    return os.environ.get("SKIP_DB_CHECK") == "true"


def should_skip_env_check():
    """
    Vérifie si les tests devraient ignorer les vérifications d'environnement.
    
    Returns:
        bool: True si les vérifications d'environnement doivent être ignorées.
    """
    return os.environ.get("SKIP_ENV_CHECK") == "true"
