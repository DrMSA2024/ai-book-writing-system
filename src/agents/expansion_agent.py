"""Content expansion agent."""

from typing import Optional
from loguru import logger

from src.agents.base_agent import BaseAgent
from src.models.chapter import Chapter
from src.models.book_profile import BookProfile
from src.api.deepseek_client import DeepSeekClient
from src.memory.memory_manager import MemoryManager


class ExpansionAgent(BaseAgent):
    """Expands chapter content to meet page targets."""

    def __init__(
        self,
        api_client: DeepSeekClient,
        memory_manager: MemoryManager,
    ):
        """Initialize expansion agent.

        Args:
            api_client: DeepSeek API client
            memory_manager: Memory manager
        """
        super().__init__(
            name="ExpansionAgent",
            description="Expands chapters to meet page targets",
            api_client=api_client,
            memory_manager=memory_manager,
        )

    async def execute(
        self,
        chapter: Chapter,
        profile: BookProfile,
        target_pages: int,
    ) -> Chapter:
        """Expand chapter content.

        Args:
            chapter: Chapter to expand
            profile: Book profile
            target_pages: Target page count

        Returns:
            Expanded chapter
        """
        self.log_info(
            f"Expanding chapter {chapter.chapter_number} to {target_pages} pages"
        )

        try:
            # Estimate current page count (roughly 250 words per page)
            current_content = chapter.get_full_content()
            current_words = len(current_content.split())
            target_words = target_pages * 250

            expansion_ratio = target_words / max(current_words, 1)

            if expansion_ratio <= 1.1:  # Within 10% of target
                self.log_info("Chapter already meets page target")
                return chapter

            self.log_info(
                f"Expanding from {current_words} to {target_words} words"
            )

            # Expand each section
            if chapter.theory:
                chapter.theory = await self._expand_section(
                    chapter.theory,
                    expansion_ratio,
                    "theoretical",
                )

            if chapter.definitions:
                chapter.definitions = await self._expand_section(
                    chapter.definitions,
                    expansion_ratio,
                    "definitional",
                )

            # Add more examples if needed
            remaining_expansion = expansion_ratio - 0.5
            if remaining_expansion > 0.1:
                new_examples = await self._generate_additional_examples(
                    chapter.title,
                    profile,
                    int(remaining_expansion * 2),
                )
                chapter.examples.extend(new_examples)

            self.log_info("Chapter expansion completed")
            return chapter

        except Exception as e:
            self.log_error(f"Expansion failed: {e}")
            raise

    async def _expand_section(
        self,
        content: str,
        expansion_ratio: float,
        content_type: str,
    ) -> str:
        """Expand a single section.

        Args:
            content: Content to expand
            expansion_ratio: How much to expand
            content_type: Type of content

        Returns:
            Expanded content
        """
        words_to_add = int(
            len(content.split()) * (expansion_ratio - 1)
        )

        if words_to_add < 100:
            return content

        prompt = f"""
Expand this {content_type} content by adding ~{words_to_add} more words.
Keep the same style and depth. Add relevant details, examples, or explanations.

Original:
{content}

Provide the expanded version:
"""

        expanded = await self.api_client.generate_text(
            prompt,
            system_prompt="You are an expert content expander. Add relevant details without repetition.",
            temperature=0.6,
            max_tokens=words_to_add + 200,
        )

        return expanded or content

    async def _generate_additional_examples(
        self,
        chapter_title: str,
        profile: BookProfile,
        count: int,
    ) -> list:
        """Generate additional examples.

        Args:
            chapter_title: Chapter title
            profile: Book profile
            count: Number of examples to generate

        Returns:
            List of examples
        """
        prompt = f"""
Generate {count} additional, diverse examples for: {chapter_title}

Subject: {profile.subject_area}

Each example should:
- Show different aspects of the topic
- Be distinct from previous examples
- Include problem and solution
- Be practical and educational
"""

        text = await self.api_client.generate_text(
            prompt,
            system_prompt="You are an educational content expert. Create diverse, practical examples.",
            temperature=0.7,
            max_tokens=1500,
        )

        return [ex.strip() for ex in text.split("\n\n") if ex.strip()]
