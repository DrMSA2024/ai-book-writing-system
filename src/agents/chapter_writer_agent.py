"""Chapter writer agent."""

from typing import List, Optional
from loguru import logger

from src.agents.base_agent import BaseAgent
from src.models.chapter import Chapter
from src.models.book_profile import BookProfile
from src.models.toc import TOCItem
from src.api.deepseek_client import DeepSeekClient
from src.memory.memory_manager import MemoryManager


class ChapterWriterAgent(BaseAgent):
    """Writes book chapters with comprehensive content."""

    def __init__(
        self,
        api_client: DeepSeekClient,
        memory_manager: MemoryManager,
    ):
        """Initialize chapter writer agent.

        Args:
            api_client: DeepSeek API client
            memory_manager: Memory manager
        """
        super().__init__(
            name="ChapterWriterAgent",
            description="Writes comprehensive book chapters",
            api_client=api_client,
            memory_manager=memory_manager,
        )

    async def execute(
        self,
        chapter_number: int,
        title: str,
        profile: BookProfile,
        toc_item: Optional[TOCItem] = None,
        previous_chapter_summary: Optional[str] = None,
    ) -> Chapter:
        """Write a complete chapter.

        Args:
            chapter_number: Chapter number
            title: Chapter title
            profile: Book profile
            toc_item: TOC item for this chapter
            previous_chapter_summary: Summary of previous chapter for continuity

        Returns:
            Completed Chapter object
        """
        self.log_info(f"Writing chapter {chapter_number}: {title}")

        try:
            chapter = Chapter(
                chapter_number=chapter_number,
                title=title,
                estimated_pages=toc_item.estimated_pages if toc_item else 20,
                writing_style=profile.writing_style,
            )

            # Generate introduction
            chapter.introduction = await self._generate_introduction(
                chapter_number, title, profile, previous_chapter_summary
            )

            # Generate theory/definitions
            if profile.book_type in ["Academic Textbook", "Research Monograph", "Technical Handbook"]:
                chapter.theory = await self._generate_theory(title, profile)
                chapter.definitions = await self._generate_definitions(title, profile)

            # Generate examples
            if profile.include_examples:
                chapter.examples = await self._generate_examples(title, profile, 2)

            # Generate exercises
            if profile.include_exercises:
                chapter.exercises = await self._generate_exercises(title, profile, 3)
                chapter.mcqs = await self._generate_mcqs(title, profile, 5)

            # Generate illustration prompts
            if profile.include_illustrations:
                chapter.illustrations_prompts = await self._generate_illustration_prompts(
                    title, 2
                )

            # Generate summary
            chapter.summary = await self._generate_summary(
                chapter.get_full_content()
            )

            # Generate references
            chapter.references = await self._generate_references(title, profile, 3)

            # Store in memory
            if self.memory_manager:
                await self.memory_manager.store_chapter(
                    profile.title, chapter
                )

            self.log_info(f"Chapter {chapter_number} completed")
            return chapter

        except Exception as e:
            self.log_error(f"Chapter writing failed: {e}")
            raise

    async def _generate_introduction(
        self,
        chapter_num: int,
        title: str,
        profile: BookProfile,
        previous_summary: Optional[str],
    ) -> str:
        """Generate chapter introduction."""
        previous_context = (
            f"\nPrevious chapter context: {previous_summary}"
            if previous_summary
            else ""
        )

        prompt = f"""
Write a comprehensive introduction for Chapter {chapter_num}: {title}

Context:
- Subject: {profile.subject_area}
- Book Type: {profile.book_type}
- Academic Level: {profile.academic_level}
- Writing Style: {profile.writing_style}{previous_context}

Write 300-400 words. Make it engaging and set the context for the chapter.
"""

        return await self.api_client.generate_text(
            prompt,
            system_prompt=f"You are an expert {profile.subject_area} writer. Write clear, engaging academic content.",
            temperature=0.7,
            max_tokens=600,
        )

    async def _generate_theory(
        self, title: str, profile: BookProfile
    ) -> str:
        """Generate theoretical content."""
        prompt = f"""
Write the core theoretical content for a chapter on {title}.

Subject: {profile.subject_area}
Academic Level: {profile.academic_level}

Include:
- Key concepts
- Theoretical frameworks
- Important principles

Write 800-1200 words.
"""

        return await self.api_client.generate_text(
            prompt,
            system_prompt="You are an expert academic writer. Explain complex concepts clearly.",
            temperature=0.6,
            max_tokens=1500,
        )

    async def _generate_definitions(
        self, title: str, profile: BookProfile
    ) -> str:
        """Generate key definitions."""
        prompt = f"""
Create a comprehensive glossary of key terms and definitions for: {title}

Subject: {profile.subject_area}

Format each definition clearly with:
- Term
- Definition
- Context/Usage

Provide 10-15 key definitions.
"""

        return await self.api_client.generate_text(
            prompt,
            system_prompt="You are a technical writer. Provide clear, concise definitions.",
            temperature=0.5,
            max_tokens=1000,
        )

    async def _generate_examples(
        self,
        title: str,
        profile: BookProfile,
        count: int = 2,
    ) -> List[str]:
        """Generate practical examples."""
        prompt = f"""
Create {count} detailed, practical examples for: {title}

Subject: {profile.subject_area}
Context: {profile.subject_area}

Each example should:
- Have a clear problem statement
- Show step-by-step solution
- Include code or detailed explanation
- Demonstrate real-world application

Make them engaging and educational.
"""

        text = await self.api_client.generate_text(
            prompt,
            system_prompt="You are an educational content writer. Create clear, practical examples.",
            temperature=0.7,
            max_tokens=1500,
        )

        return [ex.strip() for ex in text.split("\n\n") if ex.strip()]

    async def _generate_exercises(
        self,
        title: str,
        profile: BookProfile,
        count: int = 3,
    ) -> List[str]:
        """Generate practice exercises."""
        prompt = f"""
Create {count} practice exercises for: {title}

Subject: {profile.subject_area}
Difficulty: {profile.academic_level}

Each exercise should:
- Challenge the student
- Require understanding of concepts
- Be solvable with chapter material
- Include difficulty indicator

"""

        text = await self.api_client.generate_text(
            prompt,
            system_prompt="You are an academic instructor. Create challenging but fair exercises.",
            temperature=0.6,
            max_tokens=1000,
        )

        return [ex.strip() for ex in text.split("\n\n") if ex.strip()]

    async def _generate_mcqs(
        self,
        title: str,
        profile: BookProfile,
        count: int = 5,
    ) -> List[dict]:
        """Generate multiple choice questions."""
        prompt = f"""
Create {count} multiple choice questions for: {title}

Subject: {profile.subject_area}

Format as JSON array:
[
  {{
    "question": "question text",
    "options": ["A) option1", "B) option2", "C) option3", "D) option4"],
    "correct": "A",
    "explanation": "why this is correct"
  }}
]

"""

        result = await self.api_client.generate_json(
            prompt,
            system_prompt="You are a question writer. Create clear, valid multiple choice questions.",
            temperature=0.5,
            max_tokens=1000,
        )

        return result if isinstance(result, list) else []

    async def _generate_illustration_prompts(
        self, title: str, count: int = 2
    ) -> List[str]:
        """Generate image prompts for illustrations."""
        prompt = f"""
Create {count} detailed image generation prompts for illustrations related to: {title}

Each prompt should:
- Describe a clear visual concept
- Include style and composition details
- Be suitable for DALL-E/Midjourney generation
- Be educational and relevant

Format as a list.
"""

        text = await self.api_client.generate_text(
            prompt,
            system_prompt="You are an expert at creating detailed image generation prompts.",
            temperature=0.7,
            max_tokens=800,
        )

        return [p.strip() for p in text.split("\n") if p.strip()]

    async def _generate_summary(self, content: str) -> str:
        """Generate chapter summary."""
        # Truncate if too long
        content = content[:2000]

        prompt = f"""
Write a concise summary (200-300 words) of this chapter content:

{content}

Summary should:
- Highlight key points
- Recap main concepts
- Be suitable for review
"""

        return await self.api_client.generate_text(
            prompt,
            system_prompt="You are an editor. Write clear, concise summaries.",
            temperature=0.5,
            max_tokens=500,
        )

    async def _generate_references(
        self,
        title: str,
        profile: BookProfile,
        count: int = 3,
    ) -> List[str]:
        """Generate reference suggestions."""
        prompt = f"""
Suggest {count} key academic references for: {title}

Subject: {profile.subject_area}
Academic Level: {profile.academic_level}

Format as properly formatted citations:
- Author(s), Year
- Title
- Publication
- URL (if available)
"""

        text = await self.api_client.generate_text(
            prompt,
            system_prompt="You are a research librarian. Suggest relevant academic references.",
            temperature=0.5,
            max_tokens=800,
        )

        return [ref.strip() for ref in text.split("\n") if ref.strip()]
