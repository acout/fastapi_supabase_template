import uuid
from sqlmodel import Field, SQLModel
from typing import Optional, ClassVar, Dict, Tuple, List, Type
from dataclasses import dataclass
from enum import Enum # Pour lier avec nos modèles

@dataclass
class PolicyDefinition:
    using: Optional[str] = None  # Pour filtrer les lignes existantes
    check: Optional[str] = None  # Pour valider les nouvelles valeurs

class RLSModel(SQLModel):
    """Classe de base avec politiques RLS par défaut"""
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    owner_id: uuid.UUID = Field(
        foreign_key="auth.users.id", nullable=False, ondelete="CASCADE"
    )
    
    # Flag pour activer/désactiver RLS
    __rls_enabled__: ClassVar[bool] = True
    
    @classmethod
    def get_select_policy(cls) -> PolicyDefinition:
        """SELECT - besoin uniquement de USING"""
        return PolicyDefinition(
            using="""
                auth.uid() = owner_id OR
                auth.role() = 'service_role'
            """
        )
    
    @classmethod
    def get_insert_policy(cls) -> PolicyDefinition:
        """INSERT - besoin uniquement de CHECK"""
        return PolicyDefinition(
            check="""
                auth.uid() = owner_id OR
                auth.role() = 'service_role'
            """
        )
    
    @classmethod
    def get_update_policy(cls) -> PolicyDefinition:
        """UPDATE - besoin des deux"""
        return PolicyDefinition(
            using="""
                auth.uid() = owner_id OR
                auth.role() = 'service_role'
            """,
            check="""
                auth.uid() = owner_id OR
                auth.role() = 'service_role'
            """
        )
    
    @classmethod
    def get_delete_policy(cls) -> PolicyDefinition:
        """DELETE - besoin uniquement de USING"""
        return PolicyDefinition(
            using="""
                auth.uid() = owner_id OR
                auth.role() = 'service_role'
            """
        )
    
    @classmethod
    def get_policies(cls) -> Dict[str, PolicyDefinition]:
        """Retourne toutes les politiques actives"""
        policies = {}
        
        if select_policy := cls.get_select_policy():
            policies['select'] = select_policy
            
        if insert_policy := cls.get_insert_policy():
            policies['insert'] = insert_policy
            
        if update_policy := cls.get_update_policy():
            policies['update'] = update_policy
            
        if delete_policy := cls.get_delete_policy():
            policies['delete'] = delete_policy
            
        return policies

class StorageOperation(str, Enum):
    SELECT = "SELECT"
    INSERT = "INSERT"
    UPDATE = "UPDATE"
    DELETE = "DELETE"

@dataclass
class BucketPolicy:
    operation: StorageOperation
    using: Optional[str] = None
    check: Optional[str] = None
    name: Optional[str] = None

class StorageBucket:
    name: ClassVar[str]
    public: ClassVar[bool] = False
    allowed_mime_types: ClassVar[List[str]] = ["*/*"]
    max_file_size: ClassVar[int] = 50 * 1024 * 1024
    linked_model: ClassVar[Optional[Type[RLSModel]]] = None  # Modèle lié
    
    @classmethod
    def get_path_pattern(cls) -> str:
        """Pattern de chemin par défaut"""
        if cls.linked_model:
            return f"{cls.linked_model.__tablename__}/{{record_id}}/{{filename}}"
        return "{user_id}/{filename}"
    
    @classmethod
    def get_policies(cls) -> List[BucketPolicy]:
        policies = []
        
        # Politique de lecture
        select_policy = f"""(
            auth.role() = 'authenticated' AND (
                -- Propriétaire direct du fichier
                auth.uid() = owner
                -- OU bucket public
                OR bucket_id = '{cls.name}' AND {str(cls.public).lower()}
                {f'''
                -- OU accès via la table liée
                OR EXISTS (
                    SELECT 1 FROM {cls.linked_model.__tablename__} t
                    WHERE 
                        -- Le chemin commence par l'ID de l'enregistrement
                        substring(name from '{cls.name}/([^/]+)/.*') = t.id::text
                        -- Et l'utilisateur a accès à cet enregistrement
                        AND ({cls.linked_model.get_select_policy().using})
                )
                ''' if cls.linked_model else ''}
            )
        )"""
        
        policies.append(BucketPolicy(
            operation=StorageOperation.SELECT,
            name=f"{cls.name}_select",
            using=select_policy
        ))
        
        # Politique d'insertion
        insert_policy = f"""(
            auth.role() = 'authenticated' AND
            (metadata->>'size')::bigint <= {cls.max_file_size} AND
            (
                '{cls.allowed_mime_types[0]}' = '*/*' OR
                metadata->>'mimetype' IN ('{("', '").join(cls.allowed_mime_types)}')
            )
            {f'''
            -- Vérifier les droits sur l'enregistrement lié
            AND EXISTS (
                SELECT 1 FROM {cls.linked_model.__tablename__} t
                WHERE 
                    -- Le chemin doit commencer par un ID valide
                    substring(name from '{cls.name}/([^/]+)/.*') = t.id::text
                    -- Et l'utilisateur doit avoir le droit de modifier l'enregistrement
                    AND ({cls.linked_model.get_update_policy().using})
            )
            ''' if cls.linked_model else ''}
        )"""
        
        policies.append(BucketPolicy(
            operation=StorageOperation.INSERT,
            name=f"{cls.name}_insert",
            check=insert_policy
        ))
        
        # Politique de mise à jour
        update_policy = f"""(
            auth.role() = 'authenticated' AND
            auth.uid() = owner AND
            (metadata->>'size')::bigint <= {cls.max_file_size} AND
            (
                '{cls.allowed_mime_types[0]}' = '*/*' OR
                metadata->>'mimetype' IN ('{("', '").join(cls.allowed_mime_types)}')
            )
            {f'''
            -- Vérifier les droits sur l'enregistrement lié
            AND EXISTS (
                SELECT 1 FROM {cls.linked_model.__tablename__} t
                WHERE 
                    substring(name from '{cls.name}/([^/]+)/.*') = t.id::text
                    AND ({cls.linked_model.get_update_policy().using})
            )
            ''' if cls.linked_model else ''}
        )"""

        policies.append(BucketPolicy(
            operation=StorageOperation.UPDATE,
            name=f"{cls.name}_update",
            check=update_policy
        ))

        # Politique de suppression
        delete_policy = f"""(
            auth.role() = 'authenticated' AND (
                auth.uid() = owner
                {f'''
                -- OU droits via la table liée
                OR EXISTS (
                    SELECT 1 FROM {cls.linked_model.__tablename__} t
                    WHERE 
                        substring(name from '{cls.name}/([^/]+)/.*') = t.id::text
                        AND ({cls.linked_model.get_delete_policy().using})
                )
                ''' if cls.linked_model else ''}
            )
        )"""

        policies.append(BucketPolicy(
            operation=StorageOperation.DELETE,
            name=f"{cls.name}_delete",
            using=delete_policy  # Pour DELETE, on utilise USING et non WITH CHECK
        ))
        
        return policies