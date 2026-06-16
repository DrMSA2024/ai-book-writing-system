"""Table of Contents generation agent."""

from typing import List, Dict, Optional
from loguru import logger
import json

from src.agents.base_agent import BaseAgent
from src.models.toc import TableOfContents, TOCItem
from src.models.book_profile import BookProfile
from src.api.deepseek_client import DeepSeekClient
from src.memory.memory_manager import MemoryManager


class TOCAgent(BaseAgent):
    """Generates table of contents for books."""

    def __init__(
        self,
        api_client: DeepSeekClient,
        memory_manager: MemoryManager,
    ):
        """Initialize TOC agent.

        Args:
            api_client: DeepSeek API client
            memory_manager: Memory manager
        """
        super().__init__(
            name="TOCAgent",
            description="Generates comprehensive table of contents",
            api_client=api_client,
            memory_manager=memory_manager,
        )

    async def execute(
        self,
        profile: BookProfile,
        custom_structure: Optional[Dict] = None,
    ) -> TableOfContents:
        """Generate table of contents.

        Args:
            profile: Book profile
            custom_structure: Optional custom structure

        Returns:
            TableOfContents object
        """
        self.log_info(f"Generating TOC for: {profile.title}")

        try:
            if custom_structure:
                toc = await self._create_from_custom_structure(
                    profile, custom_structure
                )
            else:
                toc = await self._generate_toc(profile)

            # Store in memory
            if self.memory_manager:
                await self.memory_manager.store_toc(profile.title, toc)

            self.log_info(f"TOC generated with {toc.total_chapters} chapters")
            return toc

        except Exception as e:
            self.log_error(f"TOC generation failed: {e}")
            raise

    async def _generate_toc(self, profile: BookProfile) -> TableOfContents:
        """Generate TOC using AI.

        Args:
            profile: Book profile

        Returns:
            TableOfContents object
        """
        # Estimate chapters
        chapters_count = profile.chapters_count or (
            max(3, profile.total_pages // 30)
        )

        prompt = f"""
Create a detailed table of contents for a {profile.book_type} titled \"{profile.title}\".

Book Details:
- Subject: {profile.subject_area}
- Target Readers: {profile.target_readers}
- Pages: {profile.total_pages}
- Academic Level: {profile.academic_level}
- Writing Style: {profile.writing_style}

Generate approximately {chapters_count} chapters with 2-4 sections each.

Respond with JSON array of chapters:
[
  {{
    "chapter": 1,
    "title": "Chapter Title",
    "pages": 20,
    "sections": [
      {{"title": "Section Title", "pages": 5}}
    ]
  }}
]
"""

        try:
            result = await self.api_client.generate_json(
                prompt,
                system_prompt="You are an expert book structure designer. Create comprehensive, well-organized table of contents.",
                temperature=0.5,
                max_tokens=2000,
            )

            toc = TableOfContents(
                book_title=profile.title,
                total_chapters=len(result) if isinstance(result, list) else chapters_count,
            )

            if isinstance(result, list):
                for ch_data in result:
                    chapter = toc.add_chapter(
                        number=ch_data.get("chapter", 0),
                        title=ch_data.get("title", ""),
                        estimated_pages=ch_data.get("pages", 20),
                    )

                    # Add sections
                    for i, section_data in enumerate(
                        ch_data.get("sections", []), 1
                    ):
                        toc.add_section(
                            chapter_number=ch_data.get("chapter", 0),
                            section_number=i,
                            title=section_data.get("title", ""),
                            estimated_pages=section_data.get("pages", 5),
                        )

            return toc

        except Exception as e:
            self.log_error(f"AI TOC generation failed: {e}")
            # Return default structure
            return await self._create_default_toc(profile, chapters_count)

    async def _create_default_toc(
        self, profile: BookProfile, chapters: int
    ) -> TableOfContents:
        """Create default TOC structure.

        Args:
            profile: Book profile
            chapters: Number of chapters

        Returns:
            TableOfContents object
        """
        toc = TableOfContents(
            book_title=profile.title,
            total_chapters=chapters,
        )

        pages_per_chapter = profile.total_pages // chapters

        chapter_titles = {
            1: "Introduction",
            2: "Fundamentals",
            3: "Core Concepts",
            4: "Advanced Topics",
            5: "Case Studies",
            6: "Applications",
            7: "Best Practices",
            8: "Conclusion",
        }

        for i in range(1, chapters + 1):
            title = chapter_titles.get(i, f"Chapter {i}")
            toc.add_chapter(
                number=i,
                title=title,
                estimated_pages=pages_per_chapter,
            )

            # Add 3 sections per chapter
            for j in range(1, 4):
                toc.add_section(
                    chapter_number=i,
                    section_number=j,
                    title=f"Section {j}: {title} - Part {j}",
                    estimated_pages=pages_per_chapter // 3,
                )

        return toc

    async def _create_from_custom_structure(
        self,
        profile: BookProfile,
        custom_structure: Dict,
    ) -> TableOfContents:
        """Create TOC from custom structure.

        Args:
            profile: Book profile
            custom_structure: Custom structure dict

        Returns:
            TableOfContents object
        """
        toc = TableOfContents(
            book_title=profile.title,
            total_chapters=len(custom_structure.get("chapters", [])),
        )

        for ch_data in custom_structure.get("chapters", []):
            chapter = toc.add_chapter(
                number=ch_data.get("number"),
                title=ch_data.get("title"),
                estimated_pages=ch_data.get("pages", 20),
            )

            for section_data in ch_data.get("sections", []):
                toc.add_section(
                    chapter_number=ch_data.get("number"),
                    section_number=section_data.get("number"),
                    title=section_data.get("title"),
                    estimated_pages=section_data.get("pages", 5),
                )

        return toc

    async def modify_toc(
        self,
        toc: TableOfContents,
        operation: str,
        **params,
    ) -> TableOfContents:
        """Modify existing TOC.

        Args:
            toc: Table of contents to modify
            operation: Operation (add_chapter, delete_chapter, reorder, etc.)
            **params: Operation parameters

        Returns:
            Modified TOC
        """
        self.log_info(f"Modifying TOC: {operation}")

        if operation == "add_chapter":
            toc.add_chapter(
                number=params.get("number"),
                title=params.get("title"),
                estimated_pages=params.get("pages", 20),
            )
            toc.total_chapters += 1

        elif operation == "delete_chapter":
            chapter_num = params.get("number")
            toc.items = [item for item in toc.items if item.number != str(chapter_num)]
            toc.total_chapters -= 1

        elif operation == "reorder":
            # Reorder items based on new order
            new_order = params.get("order", [])
            reordered = []
            for idx in new_order:
                if idx < len(toc.items):
                    reordered.append(toc.items[idx])
            toc.items = reordered

        return toc
