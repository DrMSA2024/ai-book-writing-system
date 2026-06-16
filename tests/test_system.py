"""Unit tests for book writing system."""

import pytest
import asyncio
from pathlib import Path
import tempfile

from src.api.deepseek_client import DeepSeekClient
from src.api.rate_limiter import RateLimiter
from src.models.book_profile import BookProfile, BookType
from src.memory.database import DatabaseManager
from src.memory.vector_store import VectorStore
from src.utils.validators import validate_book_profile
from src.utils.text_processor import count_words, estimate_pages


class TestRateLimiter:
    """Test rate limiter."""

    @pytest.mark.asyncio
    async def test_rate_limiting(self):
        """Test rate limiting works."""
        limiter = RateLimiter(rate=2, period=1)

        # First two requests should succeed immediately
        await limiter.acquire()
        await limiter.acquire()

        # Third should be delayed
        import time
        start = time.time()
        await limiter.acquire()
        elapsed = time.time() - start

        # Should have delayed for approximately 1 second
        assert elapsed >= 0.9


class TestBookProfile:
    """Test book profile models."""

    def test_profile_creation(self):
        """Test creating book profile."""
        profile = BookProfile(
            title="Test Book",
            author="Test Author",
            subject_area="Test Subject",
            book_type=BookType.ACADEMIC_TEXTBOOK,
            total_pages=300,
        )

        assert profile.title == "Test Book"
        assert profile.author == "Test Author"
        assert profile.total_pages == 300

    def test_profile_validation(self):
        """Test profile validation."""
        profile = BookProfile(
            title="Test",
            author="Author",
            subject_area="Subject",
        )

        valid, errors = validate_book_profile(profile)
        assert valid
        assert len(errors) == 0

    def test_profile_validation_short_title(self):
        """Test validation catches short title."""
        profile = BookProfile(
            title="AB",
            author="Author",
            subject_area="Subject",
        )

        valid, errors = validate_book_profile(profile)
        assert not valid
        assert len(errors) > 0

    def test_profile_validation_short_pages(self):
        """Test validation catches too few pages."""
        profile = BookProfile(
            title="Test",
            author="Author",
            subject_area="Subject",
            total_pages=10,
        )

        valid, errors = validate_book_profile(profile)
        assert not valid


class TestDatabase:
    """Test database operations."""

    def test_database_initialization(self):
        """Test database initialization."""
        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = Path(tmpdir) / "test.db"
            db = DatabaseManager(str(db_path))

            assert db_path.exists()

    def test_add_book(self):
        """Test adding book to database."""
        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = Path(tmpdir) / "test.db"
            db = DatabaseManager(str(db_path))

            book_id = db.add_book(
                title="Test Book",
                author="Test Author",
                subject_area="Test",
                book_type="Academic",
                total_pages=300,
            )

            assert book_id > 0

            book = db.get_book(book_id)
            assert book["title"] == "Test Book"

    def test_get_all_books(self):
        """Test retrieving all books."""
        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = Path(tmpdir) / "test.db"
            db = DatabaseManager(str(db_path))

            db.add_book("Book 1", "Author 1", "Subject", "Type", 300)
            db.add_book("Book 2", "Author 2", "Subject", "Type", 250)

            books = db.get_all_books()
            assert len(books) == 2


class TestTextProcessing:
    """Test text processing utilities."""

    def test_count_words(self):
        """Test word counting."""
        text = "This is a test string with ten words in it now"
        count = count_words(text)
        assert count == 10

    def test_estimate_pages(self):
        """Test page estimation."""
        # Create text with ~250 words (1 page)
        text = " ".join(["word"] * 250)
        pages = estimate_pages(text)
        assert pages == 1

        # Create text with ~500 words (2 pages)
        text = " ".join(["word"] * 500)
        pages = estimate_pages(text)
        assert pages == 2


class TestVectorStore:
    """Test vector store operations."""

    def test_vector_store_initialization(self):
        """Test vector store initialization."""
        with tempfile.TemporaryDirectory() as tmpdir:
            store = VectorStore(tmpdir)
            assert store.persist_dir.exists()

    def test_add_documents(self):
        """Test adding documents to vector store."""
        with tempfile.TemporaryDirectory() as tmpdir:
            store = VectorStore(tmpdir)

            store.add_documents(
                collection_name="test_collection",
                documents=["Test document 1", "Test document 2"],
                ids=["doc1", "doc2"],
            )

            # Verify collection was created
            assert "test_collection" in store.collections

    def test_search_documents(self):
        """Test searching documents."""
        with tempfile.TemporaryDirectory() as tmpdir:
            store = VectorStore(tmpdir)

            store.add_documents(
                collection_name="test_collection",
                documents=[
                    "Machine learning is AI",
                    "Python is a programming language",
                    "Deep learning uses neural networks",
                ],
                ids=["doc1", "doc2", "doc3"],
            )

            results = store.search(
                collection_name="test_collection",
                query="machine learning",
                top_k=2,
            )

            assert len(results) > 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
