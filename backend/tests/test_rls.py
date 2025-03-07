import asyncio
from httpx import AsyncClient
import pytest
from supabase import create_client, Client
from uuid import UUID
import os
from dotenv import load_dotenv
from faker import Faker
from app.core.config import settings
import uuid
from app.models.profile import ProfilePicturesBucket
# Charger les variables d'environnement de test
load_dotenv(".env.test")

fake = Faker()

# Client Supabase avec service_role
supabase = create_client(
    settings.SUPABASE_URL,
    settings.SUPABASE_SERVICE_KEY
)

def create_test_user(password: str = "testpass123!") -> dict:
    """Crée un utilisateur de test via l'API admin"""
    email = fake.email()
    print(f"Creating test user with email: {email}")
    
    # Version synchrone - pas de await
    user = supabase.auth.admin.create_user({
        "email": email,
        "password": password,
        "email_confirm": True
    })
    return user

async def test_rls_policies():
    """Test des politiques RLS"""
    user1 = None
    user2 = None
    
    try:
        # Création des utilisateurs
        user1 = create_test_user()
        user2 = create_test_user()
        
        # Clients pour chaque utilisateur avec auth
        client1 = create_client(
            settings.SUPABASE_URL,
            settings.SUPABASE_KEY
        )
        auth1 = client1.auth.sign_in_with_password({
            "email": user1.user.email,
            "password": "testpass123!"
        })
        # Important: définir le token d'accès
        client1.postgrest.auth(auth1.session.access_token)
        client1.storage._client.headers["Authorization"] = f"Bearer {auth1.session.access_token}"
        
        client2 = create_client(
            settings.SUPABASE_URL,
            settings.SUPABASE_KEY
        )
        auth2 = client2.auth.sign_in_with_password({
            "email": user2.user.email,
            "password": "testpass123!"
        })
        # Important: définir le token d'accès
        client2.postgrest.auth(auth2.session.access_token)
        client2.storage._client.headers["Authorization"] = f"Bearer {auth2.session.access_token}"
        # INSERT - Chaque utilisateur crée son profil
        profile1 = client1.table("profiles").insert({
            "id": str(uuid.uuid4()),
            "owner_id": user1.user.id,
            "email": user1.user.email,
            "name": "User One"
        }).execute()
        
        profile2 = client2.table("profiles").insert({
            "id": str(uuid.uuid4()),
            "owner_id": user2.user.id,
            "email": user2.user.email,
            "name": "User Two"
        }).execute()
        
        # SELECT - Vérifier que chaque utilisateur ne voit que son profil
        profiles_user1 = client1.table("profiles").select("*").execute()
        assert len(profiles_user1.data) == 1, "User1 devrait voir uniquement son profil"
        assert profiles_user1.data[0]["owner_id"] == user1.user.id
        
        profiles_user2 = client2.table("profiles").select("*").execute()
        assert len(profiles_user2.data) == 1, "User2 devrait voir uniquement son profil"
        assert profiles_user2.data[0]["owner_id"] == user2.user.id
        
        # UPDATE - Tester la mise à jour
        # User1 essaie de mettre à jour son profil (devrait réussir)
        client1.table("profiles").update({
            "name": "User One Updated"
        }).eq("owner_id", user1.user.id).execute()
        
        # User1 essaie de mettre à jour le profil de User2 (devrait échouer)
        try:
            client1.table("profiles").update({
                "name": "Hacked!"
            }).eq("owner_id", user2.user.id).execute()
            assert False, "La mise à jour du profil d'un autre utilisateur devrait échouer"
        except Exception as e:
            print("Erreur attendue:", e)
        
        # DELETE - Tester la suppression
        # User2 essaie de supprimer le profil de User1 (devrait échouer)
        try:
            client2.table("profiles").delete().eq("owner_id", user1.user.id).execute()
            assert False, "La suppression du profil d'un autre utilisateur devrait échouer"
        except Exception as e:
            print("Erreur attendue:", e)
        
        # User2 supprime son propre profil (devrait réussir)
        client2.table("profiles").delete().eq("owner_id", user2.user.id).execute()
        
        # Vérifier que le profil de User2 est bien supprimé
        profiles_after = client2.table("profiles").select("*").execute()
        assert len(profiles_after.data) == 0, "User2 ne devrait plus voir de profil"
        
        # Test du bucket storage
        test_file = "test.jpg"
        with open(test_file, "wb") as f:
            f.write(b"fake image content")
        
        # Upload par User1
        bucket_name = "profile-pictures"
        # Important: le chemin doit suivre le format bucket_name/record_id/filename
        path1 = f"{profile1.data[0]['owner_id']}/avatar.jpg"
        client1.storage.from_(bucket_name).upload(
            path1,
            test_file,
            {
                "content-type": "image/jpeg",
                "x-upsert": "true"  # Permet de remplacer si existe
            }
        )
        
        # User2 essaie d'accéder au fichier de User1 (devrait échouer)
        try:
            client2.storage.from_(bucket_name).download(path1)
            assert False, "Le téléchargement du fichier d'un autre utilisateur devrait échouer"
        except Exception as e:
            print("Erreur attendue:", e)
        
        # Test que User1 peut accéder à son propre fichier
        try:
            url = client1.storage.from_(bucket_name).get_public_url(path1)
            assert url, "User1 devrait pouvoir accéder à son fichier"
        except Exception as e:
            assert False, f"User1 devrait pouvoir accéder à son fichier: {e}"
        
        # Nettoyage
        os.remove(test_file)
        client1.storage.from_(bucket_name).remove([path1])
        client1.table("profiles").delete().eq("owner_id", user1.user.id).execute()
    finally:
        # Nettoyage synchrone
        if user1:
            supabase.auth.admin.delete_user(user1.user.id)
        if user2:
            supabase.auth.admin.delete_user(user2.user.id)

if __name__ == "__main__":
    asyncio.run(test_rls_policies())