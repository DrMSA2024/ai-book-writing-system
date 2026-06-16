"""SQLite database management."""

import sqlite3
from pathlib import Path
from typing import List, Dict, Optional, Any
from loguru import logger
from datetime import datetime
import json


class DatabaseManager:
    """Manages SQLite database for book writing system."""

    def __init__(self, db_path: str):
        """Initialize database manager.

        Args:
            db_path: Path to SQLite database
        """
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_db()

    def _init_db(self) -> None:
        """Initialize database schema."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Books table
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS books (
                id INTEGER PRIMARY KEY,
                title TEXT NOT NULL UNIQUE,
                author TEXT NOT NULL,
                subject_area TEXT,
                book_type TEXT,
                total_pages INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                metadata TEXT
            )
        """
        )

        # Chapters table
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS chapters (
                id INTEGER PRIMARY KEY,
                book_id INTEGER NOT NULL,
                chapter_number INTEGER,
                title TEXT NOT NULL,
                content TEXT,
                word_count INTEGER,
                ai_score REAL,
                is_humanized BOOLEAN DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (book_id) REFERENCES books(id)
            )
        """
        )

        # Table of Contents
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS toc (
                id INTEGER PRIMARY KEY,
                book_id INTEGER NOT NULL,
                structure TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (book_id) REFERENCES books(id)
            )
        """
        )

        # Settings table
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS settings (
                id INTEGER PRIMARY KEY,
                book_id INTEGER NOT NULL,
                key TEXT NOT NULL,
                value TEXT,
                FOREIGN KEY (book_id) REFERENCES books(id),
                UNIQUE(book_id, key)
            )
        """
        )

        # Image prompts table
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS image_prompts (
                id INTEGER PRIMARY KEY,
                book_id INTEGER NOT NULL,
                chapter_id INTEGER,
                prompt_type TEXT,
                prompts TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (book_id) REFERENCES books(id),
                FOREIGN KEY (chapter_id) REFERENCES chapters(id)
            )
        """
        )

        conn.commit()
        conn.close()
        logger.info(f"Database initialized: {self.db_path}")

    def add_book(
        self,
        title: str,
        author: str,
        subject_area: str,
        book_type: str,
        total_pages: int,
        metadata: Optional[Dict] = None,
    ) -> int:
        """Add book to database.

        Args:
            title: Book title
            author: Author name
            subject_area: Subject area
            book_type: Book type
            total_pages: Total pages
            metadata: Optional metadata dict

        Returns:
            Book ID
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        metadata_json = json.dumps(metadata) if metadata else None

        try:
            cursor.execute(
                """
                INSERT INTO books (title, author, subject_area, book_type, total_pages, metadata)
                VALUES (?, ?, ?, ?, ?, ?)
            """,
                (title, author, subject_area, book_type, total_pages, metadata_json),
            )
            conn.commit()
            book_id = cursor.lastrowid
            logger.info(f"Book added: {title} (ID: {book_id})")
            return book_id
        except sqlite3.IntegrityError:
            logger.warning(f"Book already exists: {title}")
            cursor.execute("SELECT id FROM books WHERE title = ?", (title,))
            result = cursor.fetchone()
            return result[0] if result else -1
        finally:
            conn.close()

    def add_chapter(
        self,
        book_id: int,
        chapter_number: int,
        title: str,
        content: str,
        word_count: Optional[int] = None,
    ) -> int:
        """Add chapter to database.

        Args:
            book_id: Book ID
            chapter_number: Chapter number
            title: Chapter title
            content: Chapter content
            word_count: Word count

        Returns:
            Chapter ID
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        if word_count is None:
            word_count = len(content.split())

        cursor.execute(
            """
            INSERT INTO chapters (book_id, chapter_number, title, content, word_count)
            VALUES (?, ?, ?, ?, ?)
        """,
            (book_id, chapter_number, title, content, word_count),
        )
        conn.commit()
        chapter_id = cursor.lastrowid
        conn.close()
        return chapter_id

    def get_book(self, book_id: int) -> Optional[Dict]:
        """Get book by ID.

        Args:
            book_id: Book ID

        Returns:
            Book dict or None
        """
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM books WHERE id = ?", (book_id,))
        result = cursor.fetchone()
        conn.close()

        return dict(result) if result else None

    def get_book_by_title(self, title: str) -> Optional[Dict]:
        """Get book by title.

        Args:
            title: Book title

        Returns:
            Book dict or None
        """
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM books WHERE title = ?", (title,))
        result = cursor.fetchone()
        conn.close()

        return dict(result) if result else None

    def get_chapters(self, book_id: int) -> List[Dict]:
        """Get all chapters for a book.

        Args:
            book_id: Book ID

        Returns:
            List of chapter dicts
        """
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        cursor.execute(
            "SELECT * FROM chapters WHERE book_id = ? ORDER BY chapter_number",
            (book_id,),
        )
        results = cursor.fetchall()
        conn.close()

        return [dict(row) for row in results]

    def update_chapter_ai_score(
        self, chapter_id: int, ai_score: float, is_humanized: bool = False
    ) -> None:
        """Update chapter AI score.

        Args:
            chapter_id: Chapter ID
            ai_score: AI score
            is_humanized: Whether humanized
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute(
            "UPDATE chapters SET ai_score = ?, is_humanized = ? WHERE id = ?",
            (ai_score, is_humanized, chapter_id),
        )
        conn.commit()
        conn.close()

    def get_all_books(self) -> List[Dict]:
        """Get all books.

        Returns:
            List of book dicts
        """
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM books ORDER BY created_at DESC")
        results = cursor.fetchall()
        conn.close()

        return [dict(row) for row in results]
