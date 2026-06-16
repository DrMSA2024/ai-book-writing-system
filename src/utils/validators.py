"""Input validation utilities."""

from src.models.book_profile import BookProfile
from typing import Tuple, List


def validate_book_profile(profile: BookProfile) -> Tuple[bool, List[str]]:
    """Validate book profile.

    Args:
        profile: BookProfile to validate

    Returns:
        Tuple of (is_valid, error_messages)
    """
    errors = []

    # Validate title
    if not profile.title or len(profile.title) < 3:
        errors.append("Book title must be at least 3 characters")

    # Validate author
    if not profile.author or len(profile.author) < 2:
        errors.append("Author name must be at least 2 characters")

    # Validate pages
    if profile.total_pages < 50:
        errors.append("Book must have at least 50 pages")

    if profile.total_pages > 10000:
        errors.append("Book exceeds maximum 10000 pages")

    # Validate AI score target
    if not 0 <= profile.ai_score_target <= 1:
        errors.append("AI score target must be between 0 and 1")

    return len(errors) == 0, errors
