"""Text processing utilities."""

from typing import List
import re


def count_words(text: str) -> int:
    """Count words in text.

    Args:
        text: Text to count

    Returns:
        Word count
    """
    return len(text.split())


def split_chapters(
    text: str, num_chapters: int
) -> List[str]:
    """Split text into chapters.

    Args:
        text: Text to split
        num_chapters: Number of chapters

    Returns:
        List of chapter texts
    """
    # Split by double newlines
    paragraphs = text.split("\n\n")
    para_per_chapter = max(1, len(paragraphs) // num_chapters)

    chapters = []
    for i in range(num_chapters):
        start = i * para_per_chapter
        end = (
            (i + 1) * para_per_chapter
            if i < num_chapters - 1
            else len(paragraphs)
        )
        chapter_text = "\n\n".join(paragraphs[start:end])
        if chapter_text.strip():
            chapters.append(chapter_text)

    return chapters


def estimate_pages(text: str) -> int:
    """Estimate page count (roughly 250 words per page).

    Args:
        text: Text to estimate

    Returns:
        Estimated page count
    """
    words = count_words(text)
    return max(1, words // 250)


def sanitize_filename(filename: str) -> str:
    """Sanitize filename.

    Args:
        filename: Filename to sanitize

    Returns:
        Sanitized filename
    """
    # Replace invalid characters
    filename = re.sub(r"[^\w\s-]", "", filename)
    filename = re.sub(r"[\s_-]+", "_", filename)
    return filename.lower()
