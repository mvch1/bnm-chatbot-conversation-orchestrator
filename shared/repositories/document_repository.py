"""
FICHIER : shared/repositories/document_repository.py
RÔLE : Opérations sur les tables documentaires (sources, chunks, embeddings).

MÉTHODES — document_sources :
  get_by_filename(filename: str) → DocumentSource | None
  get_by_hash(md5_hash: str) → DocumentSource | None
    → Vérifie si un document a changé avant re-ingestion
  upsert_source(filename, title, category, hash, file_path) → DocumentSource
    → Crée ou met à jour les métadonnées d'un document

MÉTHODES — document_chunks :
  create_chunks_batch(chunks: List[ChunkCreate]) → List[DocumentChunk]
    → Insertion en batch pour l'ingestion (performance)
  delete_chunks_for_source(source_id: UUID) → int
    → Supprime les anciens chunks avant re-ingestion

MÉTHODES — document_embeddings :
  create_embeddings_batch(embeddings: List[EmbeddingCreate]) → None
    → Insertion en batch des vecteurs (optimisé pgvector)

  search_similar(query_vector: List[float], limit: int = 5,
                 min_similarity: float = 0.75) → List[SearchResult]
    → Requête de similarité cosinus via pgvector (<=> operator)
    → Retourne : content, section_title, filename, similarity_score

CONSEILS TECHNIQUES :
  - Batch insert de 100 embeddings par appel (évite les timeouts)
  - search_similar utilise l'index HNSW → latence < 50ms même sur 100K vecteurs
  - Transactionner upsert_source + delete_chunks + create_chunks en un seul commit

TECHNOLOGIE : asyncpg, pgvector, SQLAlchemy 2.0, numpy
"""
