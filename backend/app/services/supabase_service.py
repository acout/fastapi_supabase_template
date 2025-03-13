from supabase import Client, create_client

from app.core.config import settings
from app.utils.testing import MockSupabaseClient, should_mock_supabase


def get_supabase_client() -> Client:
    """Crée et retourne un client Supabase.
    
    Si MOCK_SUPABASE est activé, retourne un mock au lieu d'un client réel.
    Cela permet de tester l'application sans connexion à Supabase.
    
    Returns:
        Client: Un client Supabase ou un mock.
    """
    # Utiliser le mock si demandé
    if should_mock_supabase():
        return MockSupabaseClient()  # type: ignore
        
    # Sinon, créer un client réel
    return create_client(settings.SUPABASE_URL, settings.SUPABASE_KEY)
