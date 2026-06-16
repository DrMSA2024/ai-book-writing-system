"""File management utilities."""

import shutil
from pathlib import Path
from typing import Optional
from loguru import logger
import zipfile


class FileManager:
    """Manages file operations for book writing system."""

    def __init__(self, base_dir: Path):
        """Initialize file manager.

        Args:
            base_dir: Base directory for operations
        """
        self.base_dir = Path(base_dir)
        self.base_dir.mkdir(parents=True, exist_ok=True)

    def create_book_directory(self, book_title: str) -> Path:
        """Create directory for book.

        Args:
            book_title: Book title

        Returns:
            Path to book directory
        """
        # Sanitize title for directory name
        safe_title = book_title.replace(" ", "_").replace("/", "_")
        book_dir = self.base_dir / safe_title
        book_dir.mkdir(parents=True, exist_ok=True)

        # Create subdirectories
        (book_dir / "chapters").mkdir(exist_ok=True)
        (book_dir / "images").mkdir(exist_ok=True)
        (book_dir / "latex").mkdir(exist_ok=True)
        (book_dir / "output").mkdir(exist_ok=True)

        logger.info(f"Created book directory: {book_dir}")
        return book_dir

    def save_chapter(
        self, book_dir: Path, chapter_num: int, content: str
    ) -> Path:
        """Save chapter to file.

        Args:
            book_dir: Book directory
            chapter_num: Chapter number
            content: Chapter content

        Returns:
            Path to saved file
        """
        chapter_file = book_dir / "chapters" / f"chapter_{chapter_num:02d}.tex"
        chapter_file.write_text(content, encoding="utf-8")
        logger.info(f"Saved chapter: {chapter_file}")
        return chapter_file

    def save_latex(
        self, book_dir: Path, latex_code: str, filename: str = "main.tex"
    ) -> Path:
        """Save LaTeX file.

        Args:
            book_dir: Book directory
            latex_code: LaTeX code
            filename: Filename

        Returns:
            Path to saved file
        """
        latex_file = book_dir / "latex" / filename
        latex_file.write_text(latex_code, encoding="utf-8")
        logger.info(f"Saved LaTeX: {latex_file}")
        return latex_file

    def save_pdf(
        self, book_dir: Path, pdf_path: Path, destination: str = "output.pdf"
    ) -> Path:
        """Save PDF file.

        Args:
            book_dir: Book directory
            pdf_path: Source PDF path
            destination: Destination filename

        Returns:
            Path to saved file
        """
        output_file = book_dir / "output" / destination
        shutil.copy(pdf_path, output_file)
        logger.info(f"Saved PDF: {output_file}")
        return output_file

    def create_archive(
        self, book_dir: Path, archive_name: Optional[str] = None
    ) -> Path:
        """Create archive of book.

        Args:
            book_dir: Book directory
            archive_name: Archive filename (optional)

        Returns:
            Path to archive
        """
        if archive_name is None:
            archive_name = f"{book_dir.name}.zip"

        archive_path = self.base_dir / archive_name

        with zipfile.ZipFile(archive_path, "w", zipfile.ZIP_DEFLATED) as zf:
            for file in book_dir.rglob("*"):
                if file.is_file():
                    arcname = file.relative_to(self.base_dir)
                    zf.write(file, arcname)

        logger.info(f"Created archive: {archive_path}")
        return archive_path

    def cleanup(self, book_dir: Path) -> None:
        """Clean up temporary files.

        Args:
            book_dir: Book directory
        """
        if book_dir.exists():
            shutil.rmtree(book_dir)
            logger.info(f"Cleaned up: {book_dir}")
