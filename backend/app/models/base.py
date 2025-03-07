import uuid
from sqlmodel import Field, SQLModel
from typing import Optional, ClassVar, Dict, Tuple
from dataclasses import dataclass

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
