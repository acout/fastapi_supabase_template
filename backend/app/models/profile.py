from uuid import UUID, uuid4
from sqlmodel import Field
from typing import Optional
from .base import RLSModel, PolicyDefinition, StorageBucket
from fastapi import UploadFile

class Profile(RLSModel, table=True):
    __tablename__ = "profiles"
    __table_args__ = {"schema": "public"}
    __rls_enabled__ = True
    
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    user_id: UUID = Field(foreign_key="auth.users.id")
    email: str = Field(max_length=255)
    name: Optional[str] = Field(default=None)
    picture_path: Optional[str] = None  # Chemin dans le bucket
    
    @classmethod
    def get_select_policy(cls) -> PolicyDefinition:
        """Lecture uniquement par le propriétaire"""
        return PolicyDefinition(
            using="auth.uid() = user_id"
        )
    
    @classmethod
    def get_insert_policy(cls) -> PolicyDefinition:
        """Création par utilisateurs authentifiés"""
        return PolicyDefinition(
            check="auth.uid() = user_id AND auth.role() = 'authenticated'"
        )
    
    @classmethod
    def get_update_policy(cls) -> PolicyDefinition:
        """Mise à jour uniquement par le propriétaire"""
        return PolicyDefinition(
            using="auth.uid() = user_id",
            check="auth.uid() = user_id"
        )
    
    @classmethod
    def get_delete_policy(cls) -> PolicyDefinition:
        """Suppression uniquement par le propriétaire"""
        return PolicyDefinition(
            using="auth.uid() = user_id"
        )
    
    @property
    def picture_url(self) -> Optional[str]:
        """Génère l'URL de l'image de profil"""
        if self.picture_path:
            return f"/storage/v1/object/public/{ProfilePicturesBucket.name}/{self.picture_path}"
        return None
    
    async def upload_picture(self, file: UploadFile):
        """Upload une nouvelle image de profil"""
        path = ProfilePicturesBucket.get_path_pattern().format(
            record_id=self.id,
            filename=file.filename
        )
        
        # Upload via Supabase Storage
        await supabase.storage.from_(ProfilePicturesBucket.name).upload(
            path,
            file.file.read(),
            {"content-type": file.content_type}
        )
        
        # Mettre à jour le chemin
        self.picture_path = path
        return path

# Exemple avec un bucket lié à un modèle Profile
class ProfilePicturesBucket(StorageBucket):
    name = "profile-pictures"
    public = True
    allowed_mime_types = ["image/jpeg", "image/png", "image/webp"]
    max_file_size = 5 * 1024 * 1024  # 5MB
    linked_model = Profile  # Lien