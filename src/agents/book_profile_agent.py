"""Book profile agent for gathering book requirements."""

from typing import Optional
from loguru import logger

from src.agents.base_agent import BaseAgent
from src.models.book_profile import BookProfile, BookType, WritingStyle, AcademicLevel
from src.api.deepseek_client import DeepSeekClient
from src.memory.memory_manager import MemoryManager


class BookProfileAgent(BaseAgent):
    """Collects and validates book profile information."""

    def __init__(
        self,
        api_client: DeepSeekClient,
        memory_manager: MemoryManager,
    ):
        """Initialize book profile agent.

        Args:
            api_client: DeepSeek API client
            memory_manager: Memory manager
        """
        super().__init__(
            name="BookProfileAgent",
            description="Collects and validates book requirements from author",
            api_client=api_client,
            memory_manager=memory_manager,
        )

    async def execute(
        self,
        title: str,
        author: str,
        subject_area: str,
        book_type: str = "Academic Textbook",
        academic_level: str = "Undergraduate",
        target_readers: str = "",
        language: str = "English",
        writing_style: str = "Formal",
        total_pages: int = 300,
        **kwargs,
    ) -> BookProfile:
        """Create book profile.

        Args:
            title: Book title
            author: Author name
            subject_area: Subject area
            book_type: Type of book
            academic_level: Academic level
            target_readers: Target readers description
            language: Book language
            writing_style: Writing style
            total_pages: Total pages target
            **kwargs: Additional fields

        Returns:
            BookProfile instance
        """
        self.log_info(f"Creating profile for book: {title}")

        try:
            # Create profile
            profile = BookProfile(
                title=title,
                author=author,
                subject_area=subject_area,
                book_type=BookType(book_type),
                academic_level=AcademicLevel(academic_level),
                target_readers=target_readers or subject_area,
                language=language,
                writing_style=WritingStyle(writing_style),
                total_pages=total_pages,
                **kwargs,
            )

            # Store in memory
            if self.memory_manager:
                await self.memory_manager.store_book_profile(profile)

            self.log_info(f"Profile created successfully: {profile}")
            return profile

        except ValueError as e:
            self.log_error(f"Invalid profile parameters: {e}")
            raise
        except Exception as e:
            self.log_error(f"Profile creation failed: {e}")
            raise

    async def validate_profile(self, profile: BookProfile) -> bool:
        """Validate book profile.

        Args:
            profile: Profile to validate

        Returns:
            True if valid
        """
        self.log_info(f"Validating profile: {profile.title}")

        # Check required fields
        if not profile.title or not profile.author:
            self.log_error("Missing required fields")
            return False

        if profile.total_pages < 50:
            self.log_error("Book too short (minimum 50 pages)")
            return False

        self.log_info("Profile validation passed")
        return True

    async def get_profile_summary(self, profile: BookProfile) -> str:
        """Get human-readable profile summary.

        Args:
            profile: Profile to summarize

        Returns:
            Summary string
        """
        summary_parts = [
            f"📚 Book Profile",
            f"Title: {profile.title}",
            f"Author: {profile.author}",
            f"Type: {profile.book_type}",
            f"Subject: {profile.subject_area}",
            f"Academic Level: {profile.academic_level}",
            f"Writing Style: {profile.writing_style}",
            f"Language: {profile.language}",
            f"Target Pages: {profile.total_pages}",
            f"Target Readers: {profile.target_readers}",
        ]

        return "\n".join(summary_parts)
