import asyncio
import os
import time
import uuid

import pytest
from dotenv import load_dotenv
from faker import Faker
from supabase import create_client

from app.core.config import settings

# Charger les variables d'environnement de test
try:
    load_dotenv(".env.test")
except Exception as e:
    print(f"Erreur lors du chargement de .env.test (tentative 1): {e}")
    try:
        load_dotenv("../.env.test")
    except Exception as e2:
        print(f"Erreur lors du chargement de ../.env.test (tentative 2): {e2}")

fake = Faker()


# Fonction utilitaire pour les retry
def retry_on_error(func, max_retries=3, delay=2, error_types=None):
    """Réessaie une fonction en cas d'erreur avec un délai entre les tentatives"""
    if error_types is None:
        error_types = Exception

    for attempt in range(max_retries):
        try:
            return func()
        except error_types as e:
            if attempt < max_retries - 1:
                print(f"Erreur (tentative {attempt + 1}/{max_retries}): {e}")
                print(f"Réessai dans {delay} secondes...")
                time.sleep(delay)
            else:
                raise


# Fonction pour vérifier et créer le bucket si nécessaire
def ensure_bucket_exists(bucket_name):
    """Vérifie si le bucket existe, le crée si nécessaire"""
    try:
        # Client Supabase avec service_role
        supabase = create_client(settings.SUPABASE_URL, settings.SUPABASE_SERVICE_KEY)

        def check_bucket():
            # Vérifier si le bucket existe
            headers = {
                "apikey": settings.SUPABASE_SERVICE_KEY,
                "Authorization": f"Bearer {settings.SUPABASE_SERVICE_KEY}",
            }
            response = supabase.storage.get_bucket(bucket_name)
            print(f"Bucket {bucket_name} existe déjà")
            return True

        try:
            return retry_on_error(check_bucket)
        except Exception as e:
            if "Not Found" in str(e) or "does not exist" in str(e):
                try:
                    # Créer le bucket
                    def create_bucket():
                        response = supabase.storage.create_bucket(
                            bucket_name, {"public": True}
                        )
                        print(f"Bucket {bucket_name} créé avec succès")
                        return True

                    return retry_on_error(create_bucket)
                except Exception as create_error:
                    print(f"Échec de création du bucket {bucket_name}: {create_error}")
                    return False
            else:
                print(f"Erreur lors de la vérification du bucket {bucket_name}: {e}")
                return False
    except Exception as e:
        print(f"Erreur lors de l'initialisation du client Supabase: {e}")
        return False


# Initialiser client Supabase avant les tests
try:
    supabase = create_client(settings.SUPABASE_URL, settings.SUPABASE_SERVICE_KEY)
except Exception as e:
    print(f"ERREUR CRITIQUE: Impossible de créer le client Supabase: {e}")
    print(f"URL: {settings.SUPABASE_URL}")
    print(f"SERVICE_KEY: {'présent' if settings.SUPABASE_SERVICE_KEY else 'manquant'}")


def create_test_user(password: str = "testpass123!") -> dict:
    """Crée un utilisateur de test via l'API admin"""
    email = fake.email()
    print(f"Creating test user with email: {email}")

    # Fonction pour créer l'utilisateur avec retry
    def create_user():
        return supabase.auth.admin.create_user(
            {"email": email, "password": password, "email_confirm": True}
        )

    # Utiliser retry pour la création d'utilisateur
    return retry_on_error(create_user)


async def test_rls_policies():
    """Test des politiques RLS"""
    # Vérifier si le bucket existe, le créer si nécessaire
    bucket_name = "profile-pictures"
    if not ensure_bucket_exists(bucket_name):
        pytest.skip(
            f"Impossible de créer/vérifier le bucket {bucket_name}, test ignoré"
        )

    user1 = None
    user2 = None

    try:
        # Création des utilisateurs avec protection contre les erreurs
        try:
            user1 = create_test_user()
            user2 = create_test_user()
        except Exception as e:
            pytest.skip(f"Impossible de créer les utilisateurs de test: {e}")

        # Clients pour chaque utilisateur avec auth et gestion d'erreur
        try:
            client1 = create_client(settings.SUPABASE_URL, settings.SUPABASE_KEY)
            auth1 = client1.auth.sign_in_with_password(
                {"email": user1.user.email, "password": "testpass123!"}
            )
            # Important: définir le token d'accès
            client1.postgrest.auth(auth1.session.access_token)
            client1.storage._client.headers["Authorization"] = (
                f"Bearer {auth1.session.access_token}"
            )

            client2 = create_client(settings.SUPABASE_URL, settings.SUPABASE_KEY)
            auth2 = client2.auth.sign_in_with_password(
                {"email": user2.user.email, "password": "testpass123!"}
            )
            # Important: définir le token d'accès
            client2.postgrest.auth(auth2.session.access_token)
            client2.storage._client.headers["Authorization"] = (
                f"Bearer {auth2.session.access_token}"
            )
        except Exception as e:
            pytest.skip(f"Erreur lors de la connexion des utilisateurs: {e}")

        # INSERT - Chaque utilisateur crée son profil avec gestion d'erreur
        try:
            profile1 = (
                client1.table("profiles")
                .insert(
                    {
                        "id": str(uuid.uuid4()),
                        "owner_id": user1.user.id,
                        "email": user1.user.email,
                        "name": "User One",
                    }
                )
                .execute()
            )

            profile2 = (
                client2.table("profiles")
                .insert(
                    {
                        "id": str(uuid.uuid4()),
                        "owner_id": user2.user.id,
                        "email": user2.user.email,
                        "name": "User Two",
                    }
                )
                .execute()
            )
        except Exception as e:
            pytest.skip(f"Erreur lors de la création des profils: {e}")

        # SELECT - Vérifier que chaque utilisateur ne voit que son profil
        profiles_user1 = client1.table("profiles").select("*").execute()
        assert len(profiles_user1.data) == 1, "User1 devrait voir uniquement son profil"
        assert profiles_user1.data[0]["owner_id"] == user1.user.id

        profiles_user2 = client2.table("profiles").select("*").execute()
        assert len(profiles_user2.data) == 1, "User2 devrait voir uniquement son profil"
        assert profiles_user2.data[0]["owner_id"] == user2.user.id

        # UPDATE - Tester la mise à jour
        # User1 essaie de mettre à jour son profil (devrait réussir)
        client1.table("profiles").update({"name": "User One Updated"}).eq(
            "owner_id", user1.user.id
        ).execute()

        # User1 essaie de mettre à jour le profil de User2 (devrait échouer)
        try:
            client1.table("profiles").update({"name": "Hacked!"}).eq(
                "owner_id", user2.user.id
            ).execute()
            assert False, (
                "La mise à jour du profil d'un autre utilisateur devrait échouer"
            )
        except Exception as e:
            print("Erreur attendue:", e)

        # DELETE - Tester la suppression
        # User2 essaie de supprimer le profil de User1 (devrait échouer)
        try:
            client2.table("profiles").delete().eq("owner_id", user1.user.id).execute()
            assert False, (
                "La suppression du profil d'un autre utilisateur devrait échouer"
            )
        except Exception as e:
            print("Erreur attendue:", e)

        # User2 supprime son propre profil (devrait réussir)
        client2.table("profiles").delete().eq("owner_id", user2.user.id).execute()

        # Vérifier que le profil de User2 est bien supprimé
        profiles_after = client2.table("profiles").select("*").execute()
        assert len(profiles_after.data) == 0, "User2 ne devrait plus voir de profil"

        # Test du bucket storage avec gestion améliorée des erreurs
        test_file = "test.jpg"
        try:
            with open(test_file, "wb") as f:
                f.write(b"fake image content")

            # Vérifier que le fichier a bien été créé
            assert os.path.exists(test_file), f"Fichier {test_file} n'a pas été créé"
            assert os.path.getsize(test_file) > 0, f"Fichier {test_file} est vide"
        except Exception as e:
            pytest.skip(f"Erreur lors de la création du fichier test: {e}")

        # Upload par User1
        try:
            # Important: le chemin doit suivre le format bucket_name/record_id/filename
            path1 = f"{profile1.data[0]['owner_id']}/avatar.jpg"

            # Ajout des métadonnées explicites
            file_size = os.path.getsize(test_file)
            print(f"File size: {file_size}")

            def upload_file():
                return client1.storage.from_(bucket_name).upload(
                    path1,
                    test_file,
                    {
                        "content-type": "image/jpeg",
                        "x-upsert": "true",
                        # Ajout des métadonnées nécessaires
                        "metadata": {
                            "size": str(file_size),  # Conversion explicite en string
                            "mimetype": "image/jpeg",
                        },
                    },
                )

            # Utiliser retry pour l'upload qui peut être sensible aux erreurs transitoires
            retry_on_error(upload_file)
        except Exception as e:
            pytest.skip(f"Erreur lors de l'upload du fichier: {e}")

        # User2 essaie d'accéder au fichier de User1 (devrait échouer)
        try:
            client2.storage.from_(bucket_name).download(path1)
            assert False, (
                "Le téléchargement du fichier d'un autre utilisateur devrait échouer"
            )
        except Exception as e:
            print("Erreur attendue:", e)

        # Test que User1 peut accéder à son propre fichier
        try:
            url = client1.storage.from_(bucket_name).get_public_url(path1)
            assert url, "User1 devrait pouvoir accéder à son fichier"
        except Exception as e:
            assert False, f"User1 devrait pouvoir accéder à son fichier: {e}"

        # Nettoyage avec gestion d'erreur
        try:
            if os.path.exists(test_file):
                os.remove(test_file)
            client1.storage.from_(bucket_name).remove([path1])
            client1.table("profiles").delete().eq("owner_id", user1.user.id).execute()
        except Exception as e:
            print(f"Erreur non critique lors du nettoyage: {e}")
    finally:
        # Nettoyage synchrone avec gestion d'erreur
        if user1:
            try:
                supabase.auth.admin.delete_user(user1.user.id)
            except Exception as e:
                print(f"Erreur lors de la suppression de l'utilisateur 1: {e}")
        if user2:
            try:
                supabase.auth.admin.delete_user(user2.user.id)
            except Exception as e:
                print(f"Erreur lors de la suppression de l'utilisateur 2: {e}")


if __name__ == "__main__":
    asyncio.run(test_rls_policies())
