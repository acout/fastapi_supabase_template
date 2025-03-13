import pytest
from app.utils.testing import MockSupabaseClient


def test_mock_supabase_client_basic():
    """Test de base pour vérifier que le MockSupabaseClient est instanciable."""
    client = MockSupabaseClient()
    assert client is not None


def test_mock_table_operations():
    """Test des opérations de table du MockSupabaseClient."""
    client = MockSupabaseClient()
    table = client.from_table("some_table")
    
    # Test des méthodes de base
    assert table.select() is table
    assert table.eq("column", "value") is table
    
    # Test d'exécution
    result = table.execute()
    assert "data" in result
    assert "error" in result
    assert result["error"] is None


def test_mock_auth_operations():
    """Test des opérations d'authentification du MockSupabaseClient."""
    client = MockSupabaseClient()
    
    # Test sign in
    signin_result = client.auth.sign_in({"email": "test@example.com", "password": "password"})
    assert "user" in signin_result
    assert "session" in signin_result
    assert "access_token" in signin_result["session"]
    
    # Test sign up
    signup_result = client.auth.sign_up({"email": "new@example.com", "password": "password"})
    assert signup_result is not None


def test_mock_storage_operations():
    """Test des opérations de stockage du MockSupabaseClient."""
    client = MockSupabaseClient()
    storage = client.storage.from_("bucket_name")
    
    # Test upload
    upload_result = storage.upload("path", b"file_content")
    assert "data" in upload_result
    assert "error" in upload_result
    assert "path" in upload_result["data"]
    
    # Test get public URL
    url = storage.get_public_url("path")
    assert url.startswith("https://")


def test_mock_functions():
    """Test des fonctions stockées du MockSupabaseClient."""
    client = MockSupabaseClient()
    
    # Test invoke
    result = client.functions.invoke("function_name", {"param": "value"})
    assert "data" in result
    assert "error" in result
    assert result["error"] is None
