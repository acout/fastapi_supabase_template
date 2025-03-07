import asyncio
from httpx import AsyncClient
import pytest
from supabase import create_client, Client
from uuid import UUID
import os
from dotenv import load_dotenv
from faker import Faker
from app.core.config import settings

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
        # Création synchrone des utilisateurs
        user1 = create_test_user()
        user2 = create_test_user()
        
        # Clients pour chaque utilisateur
        client1 = create_client(
            settings.SUPABASE_URL,
            settings.SUPABASE_KEY
        )
        client1.auth.sign_in_with_password({
            "email": user1.user.email,
            "password": "testpass123!"
        })
        
        client2 = create_client(
            settings.SUPABASE_URL,
            settings.SUPABASE_KEY
        )
        client2.auth.sign_in_with_password({
            "email": user2.user.email,
            "password": "testpass123!"
        })
        
        # 3. Test des opérations CRUD
        
        # INSERT - Chaque utilisateur crée son profil
        profile1 = await client1.table("profiles").insert({
            "user_id": user1.user.id,
            "email": user1.user.email,
            "name": "User One"
        }).execute()
        
        profile2 = await client2.table("profiles").insert({
            "user_id": user2.user.id,
            "email": user2.user.email,
            "name": "User Two"
        }).execute()
        
        # SELECT - Vérifier que chaque utilisateur ne voit que son profil
        profiles_user1 = await client1.table("profiles").select("*").execute()
        assert len(profiles_user1.data) == 1, "User1 devrait voir uniquement son profil"
        assert profiles_user1.data[0]["user_id"] == user1.user.id
        
        profiles_user2 = await client2.table("profiles").select("*").execute()
        assert len(profiles_user2.data) == 1, "User2 devrait voir uniquement son profil"
        assert profiles_user2.data[0]["user_id"] == user2.user.id
        
        # UPDATE - Tester la mise à jour
        # User1 essaie de mettre à jour son profil (devrait réussir)
        await client1.table("profiles").update({
            "name": "User One Updated"
        }).eq("user_id", user1.user.id).execute()
        
        # User1 essaie de mettre à jour le profil de User2 (devrait échouer)
        try:
            await client1.table("profiles").update({
                "name": "Hacked!"
            }).eq("user_id", user2.user.id).execute()
            assert False, "La mise à jour du profil d'un autre utilisateur devrait échouer"
        except Exception as e:
            print("Erreur attendue:", e)
        
        # DELETE - Tester la suppression
        # User2 essaie de supprimer le profil de User1 (devrait échouer)
        try:
            await client2.table("profiles").delete().eq("user_id", user1.user.id).execute()
            assert False, "La suppression du profil d'un autre utilisateur devrait échouer"
        except Exception as e:
            print("Erreur attendue:", e)
        
        # User2 supprime son propre profil (devrait réussir)
        await client2.table("profiles").delete().eq("user_id", user2.user.id).execute()
        
        # Vérifier que le profil de User2 est bien supprimé
        profiles_after = await client2.table("profiles").select("*").execute()
        assert len(profiles_after.data) == 0, "User2 ne devrait plus voir de profil"
        
        # Test du bucket storage
        test_file = "test.jpg"
        with open(test_file, "wb") as f:
            f.write(b"fake image content")
        
        # Upload par User1
        path1 = f"{profile1.data[0]['id']}/avatar.jpg"
        await client1.storage.from_("profile-pictures").upload(
            path1,
            test_file,
            {"content-type": "image/jpeg"}
        )
        
        # User2 essaie d'accéder au fichier de User1 (devrait échouer)
        try:
            await client2.storage.from_("profile-pictures").download(path1)
            assert False, "Le téléchargement du fichier d'un autre utilisateur devrait échouer"
        except Exception as e:
            print("Erreur attendue:", e)
        
        # Nettoyage
        os.remove(test_file)
        await client1.storage.from_("profile-pictures").remove([path1])
        await client1.table("profiles").delete().eq("user_id", user1.user.id).execute()
    finally:
        # Nettoyage synchrone
        if user1:
            supabase.auth.admin.delete_user(user1.user.id)
        if user2:
            supabase.auth.admin.delete_user(user2.user.id)

if __name__ == "__main__":
    asyncio.run(test_rls_policies()) 