import os
from unittest.mock import MagicMock

class MockSupabaseClient:
    """
    Mock pour le client Supabase utilisé dans les tests.
    Permet de tester l'application sans connexion réelle à Supabase.
    
    Usage:
        if os.environ.get("MOCK_SUPABASE") == "true":
            supabase_client = MockSupabaseClient()
        else:
            supabase_client = create_actual_supabase_client()
    """
    
    def __init__(self):
        # Simuler les tables principales avec des opérations mock
        self.table = MagicMock()
        self.table.select.return_value = self.table
        self.table.eq.return_value = self.table
        self.table.execute.return_value = {"data": [], "error": None}
        
        # Simulation de l'authentification
        self.auth = MagicMock()
        self.auth.sign_in.return_value = {"user": {"id": "mock-user-id"}, "session": {"access_token": "mock-token"}}
        self.auth.sign_in_with_password.return_value = MagicMock(user=MagicMock(id="mock-user-id"),
                                                         session=MagicMock(access_token="mock-token")) 
        self.auth.sign_up.return_value = MagicMock(user=MagicMock(id="mock-user-id", email="mock@example.com"),
                                            session=MagicMock(access_token="mock-token"))
        
        # Simulation des fonctions stockées
        self.functions = MagicMock()
        self.functions.invoke.return_value = {"data": {}, "error": None}
        
        # Simulation du stockage
        self.storage = MagicMock()
        self.storage.from_.return_value = self.storage
        self.storage.upload.return_value = {"data": {"path": "mock-path"}, "error": None}
        self.storage.get_public_url.return_value = "https://mock-storage-url.com/mock-path"
    
    def from_table(self, table_name):
        """Simuler l'accès à une table."""
        return self.table
        
    def from_(self, bucket_name):
        """Simuler l'accès à un bucket de stockage."""
        return self.storage
        
    def table(self, table_name):
        """Simuler l'accès à une table."""
        return self.table


def should_skip_db_check():
    """Vérifier si les tests doivent ignorer la vérification de connexion à la base de données."""
    return os.environ.get("SKIP_DB_CHECK", "").lower() in ("true", "1", "yes")


def should_mock_supabase():
    """Vérifier si Supabase doit être mocké pour les tests."""
    return os.environ.get("MOCK_SUPABASE", "").lower() in ("true", "1", "yes")


def should_skip_env_check():
    """Vérifier si les tests doivent ignorer la vérification des variables d'environnement."""
    return os.environ.get("SKIP_ENV_CHECK", "").lower() in ("true", "1", "yes")
