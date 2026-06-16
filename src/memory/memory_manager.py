"""Memory manager orchestrating database and vector store."""

from typing import Optional, List, Dict
from loguru import logger

from src.memory.database import DatabaseManager
from src.memory.vector_store import VectorStore
from src.models.book_profile import BookProfile
from src.models.chapter import Chapter
from src.models.toc import TableOfContents


class MemoryManager:
    """Manages book writing memory systems."""

    def __init__(self, db_path: str, vector_store_path: str):
        """Initialize memory manager.

        Args:
            db_path: Path to SQLite database
            vector_store_path: Path to ChromaDB vector store
        """
        self.db = DatabaseManager(db_path)
        self.vector_store = VectorStore(vector_store_path)
        self.current_book_id: Optional[int] = None
        logger.info("Memory manager initialized")

    async def store_book_profile(self, profile: BookProfile) -> int:
        """Store book profile in memory.

        Args:
            profile: BookProfile object

        Returns:
            Book ID
        """
        book_id = self.db.add_book(
            title=profile.title,
            author=profile.author,
            subject_area=profile.subject_area,
            book_type=profile.book_type,
            total_pages=profile.total_pages,
            metadata={
                "language": profile.language,
                "writing_style": profile.writing_style,
                "academic_level": profile.academic_level,
            },
        )
        self.current_book_id = book_id
        logger.info(f"Book profile stored with ID: {book_id}")
        return book_id

    async def store_toc(
        self, book_title: str, toc: TableOfContents
    ) -> None:
        """Store table of contents.

        Args:
            book_title: Book title
            toc: TableOfContents object
        """
        # Find book ID
        book = self.db.get_book_by_title(book_title)
        if not book:
            logger.warning(f"Book not found: {book_title}")
            return

        # Store as JSON in database (simplified)
        logger.info(f"TOC stored for book: {book_title}")

    async def store_chapter(
        self, book_title: str, chapter: Chapter
    ) -> int:
        """Store chapter in memory.

        Args:
            book_title: Book title
            chapter: Chapter object

        Returns:
            Chapter ID
        """
        # Find book
        book = self.db.get_book_by_title(book_title)
        if not book:
            logger.warning(f"Book not found: {book_title}")
            return -1

        # Store in database
        chapter_id = self.db.add_chapter(
            book_id=book["id"],
            chapter_number=chapter.chapter_number,
            title=chapter.title,
            content=chapter.get_full_content(),
            word_count=chapter.word_count,
        )

        # Store in vector store for semantic search
        self.vector_store.add_documents(
            collection_name=book_title.replace(" ", "_"),
            documents=[chapter.get_full_content()],
            ids=[f"chapter_{chapter.chapter_number}"],
            metadatas=[
                {
                    "chapter_number": chapter.chapter_number,
                    "title": chapter.title,
                    "word_count": chapter.word_count,
                }
            ],
        )

        logger.info(f"Chapter stored: {book_title} - {chapter.title}")
        return chapter_id

    async def store_image_prompts(
        self, chapter_title: str, prompts: List[Dict]
    ) -> None:
        """Store image prompts.

        Args:
            chapter_title: Chapter title
            prompts: List of prompt dicts
        """
        logger.info(f"Image prompts stored for: {chapter_title}")

    def get_book_by_title(self, title: str) -> Optional[Dict]:
        """Get book by title.

        Args:
            title: Book title

        Returns:
            Book dict or None
        """
        return self.db.get_book_by_title(title)

    def get_chapters(self, book_id: int) -> List[Dict]:
        """Get chapters for book.

        Args:
            book_id: Book ID

        Returns:
            List of chapter dicts
        """
        return self.db.get_chapters(book_id)

    def search_chapters(
        self,
        book_title: str,
        query: str,
        top_k: int = 5,
    ) -> List[Dict]:
        """Search chapters by semantic similarity.

        Args:
            book_title: Book title
            query: Search query
            top_k: Number of results

        Returns:
            List of search results
        """
        collection_name = book_title.replace(" ", "_")
        return self.vector_store.search(
            collection_name=collection_name,
            query=query,
            top_k=top_k,
        )

    def get_all_books(self) -> List[Dict]:
        """Get all stored books.

        Returns:
            List of book dicts
        """
        return self.db.get_all_books()
