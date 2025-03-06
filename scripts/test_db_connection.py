import os
from dotenv import load_dotenv
import psycopg2
from urllib.parse import quote_plus

def test_connection():
    # 1. Charger et afficher les variables d'environnement
    env_path = os.path.join(os.getcwd(), '.env')
    load_dotenv(env_path)
    
    # 2. Récupérer les paramètres
    db_params = {
        "host": os.getenv("POSTGRES_SERVER"),
        "port": os.getenv("POSTGRES_PORT", "5432"),
        "database": os.getenv("POSTGRES_DB"),
        "user": os.getenv("POSTGRES_USER"),
        "password": os.getenv("POSTGRES_PASSWORD")
    }
    
    # 3. Afficher les paramètres (sans le mot de passe)
    print("🔍 Paramètres de connexion :")
    for key, value in db_params.items():
        if key != "password":
            print(f"{key}: {value}")
    
    # 4. Construire l'URL de connexion
    password_escaped = quote_plus(db_params["password"]) if db_params["password"] else ""
    connection_url = f"postgresql://{db_params['user']}:{password_escaped}@{db_params['host']}:{db_params['port']}/{db_params['database']}"
    print("\n🔗 URL de connexion (masquée) :")
    masked_url = connection_url.replace(password_escaped, "****")
    print(masked_url)
    
    # 5. Tester la connexion
    print("\n🔌 Test de connexion :")
    try:
        conn = psycopg2.connect(
            host=db_params["host"],
            port=db_params["port"],
            database=db_params["database"],
            user=db_params["user"],
            password=db_params["password"]
        )
        print("✅ Connexion réussie !")
        
        # 6. Vérifier les permissions
        cur = conn.cursor()
        cur.execute("SELECT current_user, current_database(), version();")
        user, db, version = cur.fetchone()
        print("\n📊 Informations de connexion :")
        print(f"Utilisateur connecté : {user}")
        print(f"Base de données : {db}")
        print(f"Version PostgreSQL : {version.split(',')[0]}")
        
        cur.close()
        conn.close()
        
    except psycopg2.Error as e:
        print("❌ Erreur de connexion :")
        print(f"Code : {e.pgcode}")
        print(f"Message : {e.pgerror}")
        print("\n🔍 Diagnostic :")
        if "password authentication failed" in str(e):
            print("→ Le mot de passe semble incorrect")
        elif "connection to server" in str(e):
            print("→ Impossible d'atteindre le serveur. Vérifiez :")
            print("  - L'URL du serveur")
            print("  - Le port")
            print("  - Les règles de firewall/réseau")
        else:
            print("→ Erreur non identifiée, voir le message complet :")
            print(str(e))

if __name__ == "__main__":
    test_connection() 