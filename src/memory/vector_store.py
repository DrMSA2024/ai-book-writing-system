"""ChromaDB Vector store for semantic search."""

from typing import List, Dict, Optional
from loguru import logger
import chromadb
from chromadb.config import Settings
from pathlib import Path


class VectorStore:
    """Vector store for semantic search using ChromaDB."""

    def __init__(self, persist_dir: str):
        """Initialize vector store.

        Args:
            persist_dir: Directory for persistent storage
        """
        self.persist_dir = Path(persist_dir)
        self.persist_dir.mkdir(parents=True, exist_ok=True)

        # Initialize ChromaDB client
        settings = Settings(
            chroma_db_impl="duckdb+parquet",
            persist_directory=str(self.persist_dir),
            anonymized_telemetry=False,
        )

        self.client = chromadb.Client(settings)
        self.collections: Dict[str, any] = {}
        logger.info(f"Vector store initialized at {self.persist_dir}")

    def get_or_create_collection(self, name: str) -> any:
        """Get or create collection.

        Args:
            name: Collection name

        Returns:
            Collection object
        """
        if name not in self.collections:
            try:
                self.collections[name] = self.client.get_collection(
                    name=name
                )
            except:
                self.collections[name] = self.client.create_collection(
                    name=name,
                    metadata={"hnsw:space": "cosine"},
                )
        return self.collections[name]

    def add_documents(
        self,
        collection_name: str,
        documents: List[str],
        ids: List[str],
        metadatas: Optional[List[Dict]] = None,
    ) -> None:
        """Add documents to collection.

        Args:
            collection_name: Collection name
            documents: List of document texts
            ids: List of unique IDs
            metadatas: Optional list of metadata dicts
        """
        collection = self.get_or_create_collection(collection_name)

        collection.add(
            documents=documents,
            ids=ids,
            metadatas=metadatas or [{} for _ in documents],
        )

        logger.info(
            f"Added {len(documents)} documents to {collection_name}"
        )

    def search(
        self,
        collection_name: str,
        query: str,
        top_k: int = 5,
    ) -> List[Dict]:
        """Search collection.

        Args:
            collection_name: Collection name
            query: Search query
            top_k: Number of results

        Returns:
            List of results
        """
        collection = self.get_or_create_collection(collection_name)

        results = collection.query(
            query_texts=[query],
            n_results=top_k,
        )

        # Format results
        formatted_results = []
        if results and results["documents"]:
            for i, doc in enumerate(results["documents"][0]):
                formatted_results.append(
                    {
                        "id": results["ids"][0][i]
                        if results["ids"][0]
                        else None,
                        "document": doc,
                        "distance": results["distances"][0][i]
                        if results["distances"][0]
                        else None,
                        "metadata": results["metadatas"][0][i]
                        if results["metadatas"][0]
                        else {},
                    }
                )

        return formatted_results

    def delete_collection(self, collection_name: str) -> None:
        """Delete collection.

        Args:
            collection_name: Collection name
        """
        try:
            self.client.delete_collection(name=collection_name)
            if collection_name in self.collections:
                del self.collections[collection_name]
            logger.info(f"Deleted collection: {collection_name}")
        except Exception as e:
            logger.error(f"Failed to delete collection: {e}")

    def clear_all(self) -> None:
        """Clear all collections."""
        for name in list(self.collections.keys()):
            self.delete_collection(name)
        logger.info("Cleared all collections")
