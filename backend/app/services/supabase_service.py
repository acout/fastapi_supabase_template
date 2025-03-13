from supabase import Client, create_client

from app.core.config import settings


def get_supabase_client() -> Client:
    """Crée et retourne un client Supabase.
    
    Returns:
        Client: Un client Supabase pour interagir avec l'API Supabase.
    """
    return create_client(settings.SUPABASE_URL, settings.SUPABASE_KEY)
