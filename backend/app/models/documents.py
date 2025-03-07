from sqlmodel import SQLModel, Field
from uuid import UUID, uuid4
from typing import Optional, List
from .base import RLSModel
from .storage import StorageBucket
from pgvector.sqlalchemy import Vector

class DocumentsBucket(StorageBucket):
    name = "documents"
    public = False
    allowed_mime_types = [
        "application/pdf",
        "application/msword",
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        "text/plain"
    ]
    max_file_size = 50 * 1024 * 1024  # 50MB

class Document(RLSModel, table=True):
    """Document original"""
    __tablename__ = "documents"
    
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    user_id: UUID = Field(foreign_key="auth.users.id")
    organization_id: Optional[UUID] = Field(foreign_key="organizations.id")
    
    title: str
    file_path: str  # Chemin dans le bucket
    mime_type: str
    file_size: int
    
    # Métadonnées extraites
    total_pages: Optional[int] = None
    language: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    processed_at: Optional[datetime] = None
    
    async def upload_file(self, file: UploadFile) -> str:
        """Upload le document original"""
        path = f"{self.id}/{file.filename}"
        await supabase.storage.from_(DocumentsBucket.name).upload(
            path,
            file.file.read(),
            {"content-type": file.content_type}
        )
        self.file_path = path
        self.mime_type = file.content_type
        return path
    
    async def get_content(self) -> bytes:
        """Récupère le contenu brut du document"""
        return await supabase.storage.from_(DocumentsBucket.name).download(self.file_path)

class DocumentChunk(RLSModel, table=True):
    """Chunk de texte extrait"""
    __tablename__ = "document_chunks"
    __table_args__ = (
        sa.Index('idx_document_chunks_embedding', 'embedding', postgresql_using='ivfflat'),
    )
    
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    document_id: UUID = Field(foreign_key="documents.id")
    
    # Contenu du chunk directement en base
    content: str = Field(max_length=8192)  # Limité à 8KB
    chunk_index: int  # Position dans le document
    page_number: Optional[int] = None
    
    # Embedding vectoriel (utilisation de pgvector)
    embedding: Optional[List[float]] = Field(sa_column=Column(Vector(1536)))  # Pour OpenAI
    
    @classmethod
    def get_select_policy(cls) -> str:
        """Hérite des permissions du document parent"""
        return """
            EXISTS (
                SELECT 1 FROM documents d
                WHERE d.id = document_chunks.document_id
                AND (
                    d.user_id = auth.uid() OR
                    auth.role() = 'service_role' OR
                    EXISTS (
                        SELECT 1 FROM organizations_users ou
                        WHERE ou.user_id = auth.uid()
                        AND ou.organization_id = d.organization_id
                    )
                )
            )
        """

# Service pour gérer le processing
class DocumentProcessor:
    def __init__(self, document: Document):
        self.document = document
    
    async def process(self):
        """Process un document complet"""
        # Récupérer le contenu
        content = await self.document.get_content()
        
        # Extraire le texte selon le type
        if self.document.mime_type == 'application/pdf':
            text = self._extract_pdf_text(content)
        elif 'wordprocessing' in self.document.mime_type:
            text = self._extract_docx_text(content)
        else:
            text = content.decode('utf-8')
        
        # Chunking
        chunks = self._create_chunks(text)
        
        # Créer les chunks en base
        for i, chunk_text in enumerate(chunks):
            chunk = DocumentChunk(
                document_id=self.document.id,
                content=chunk_text,
                chunk_index=i
            )
            # Générer l'embedding
            chunk.embedding = await self._generate_embedding(chunk_text)
            
            # Sauvegarder
            db.add(chunk)
        
        self.document.processed_at = datetime.utcnow()
        await db.commit()
    
    def _create_chunks(self, text: str) -> List[str]:
        """Découpe le texte en chunks"""
        # Utiliser une bibliothèque comme LangChain pour le chunking
        return text_splitter.split_text(text)
    
    async def _generate_embedding(self, text: str) -> List[float]:
        """Génère l'embedding pour un chunk"""
        response = await openai.Embedding.create(
            input=text,
            model="text-embedding-ada-002"
        )
        return response['data'][0]['embedding']

# API Routes
@router.post("/documents")
async def upload_document(
    file: UploadFile,
    organization_id: Optional[UUID] = None,
    current_user: User = Depends(get_current_user)
):
    # Créer le document
    doc = Document(
        user_id=current_user.id,
        organization_id=organization_id,
        title=file.filename
    )
    
    # Upload le fichier
    await doc.upload_file(file)
    
    # Lancer le processing en background
    processor = DocumentProcessor(doc)
    background_tasks.add_task(processor.process)
    
    return doc

@router.get("/documents/{document_id}/search")
async def search_document(
    document_id: UUID,
    query: str,
    current_user: User = Depends(get_current_user)
):
    # Générer l'embedding de la requête
    query_embedding = await generate_embedding(query)
    
    # Recherche vectorielle
    chunks = await db.execute("""
        SELECT *, (embedding <=> :query_embedding) as distance
        FROM document_chunks
        WHERE document_id = :document_id
        ORDER BY embedding <=> :query_embedding
        LIMIT 5
    """, {
        "document_id": document_id,
        "query_embedding": query_embedding
    })
    
    return chunks 