class Settings(BaseSettings):
    # ... autres settings ...
    SUPABASE_URL: str
    SUPABASE_KEY: str
    SUPABASE_SERVICE_KEY: str  # Ajout de la service key
    
    class Config:
        case_sensitive = True 