from typing import Annotated

from fastapi import Depends
from sqlmodel import Session

from app.core.auth import get_current_user, get_super_client
from app.core.db import get_db
from app.schemas.auth import UserIn
from app.services import get_storage_service
from app.services.storage import StorageService

CurrentUser = Annotated[UserIn, Depends(get_current_user)]
SessionDep = Annotated[Session, Depends(get_db)]
# Ne pas typer pour éviter le problème de sérialisation FastAPI
SupabaseClientDep = Depends(get_super_client)


async def get_storage_service_dep(supabase_client=SupabaseClientDep) -> StorageService:
    """Dépendance pour injecter le service de stockage"""
    return await get_storage_service(supabase_client)


StorageServiceDep = Annotated[StorageService, Depends(get_storage_service_dep)]
