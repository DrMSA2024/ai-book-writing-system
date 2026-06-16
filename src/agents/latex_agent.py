"""LaTeX generation agent."""

from typing import List, Optional
from loguru import logger

from src.agents.base_agent import BaseAgent
from src.models.latex_document import LaTeXDocument, LaTeXTemplate
from src.models.chapter import Chapter
from src.models.book_profile import BookProfile
from src.api.deepseek_client import DeepSeekClient
from src.memory.memory_manager import MemoryManager


class LaTeXAgent(BaseAgent):
    """Generates LaTeX code for books."""

    def __init__(
        self,
        api_client: DeepSeekClient,
        memory_manager: MemoryManager,
    ):
        """Initialize LaTeX agent.

        Args:
            api_client: DeepSeek API client
            memory_manager: Memory manager
        """
        super().__init__(
            name="LaTeXAgent",
            description="Generates complete LaTeX documents",
            api_client=api_client,
            memory_manager=memory_manager,
        )

    async def execute(
        self,
        profile: BookProfile,
        chapters: List[Chapter],
        template: str = "book",
    ) -> LaTeXDocument:
        """Generate LaTeX document.

        Args:
            profile: Book profile
            chapters: List of chapters
            template: LaTeX template to use

        Returns:
            LaTeXDocument object
        """
        self.log_info(f"Generating LaTeX for: {profile.title}")

        try:
            # Create document
            doc = LaTeXDocument(
                title=profile.title,
                author=profile.author,
                template=LaTeXTemplate(template),
                subject=profile.subject_area,
                keywords=[profile.subject_area, profile.book_type],
            )

            # Add packages based on content
            doc.packages = await self._get_required_packages(profile, chapters)

            # Convert chapters to LaTeX
            for chapter in chapters:
                chapter_latex = await self._chapter_to_latex(chapter, profile)
                doc.add_chapter(chapter_latex)

            # Add bibliography if needed
            if profile.include_bibliography:
                doc.bibliography_file = "references"
                doc.bibliography_style = "plain"

            if profile.include_index:
                doc.has_index = True

            if profile.include_glossary:
                doc.has_glossary = True

            self.log_info("LaTeX generation completed")
            return doc

        except Exception as e:
            self.log_error(f"LaTeX generation failed: {e}")
            raise

    async def _get_required_packages(
        self,
        profile: BookProfile,
        chapters: List[Chapter],
    ) -> List[str]:
        """Determine required LaTeX packages.

        Args:
            profile: Book profile
            chapters: List of chapters

        Returns:
            List of package names
        """
        packages = [
            "amsmath",
            "amssymb",
            "graphicx",
            "hyperref",
            "xcolor",
            "fancyhdr",
            "geometry",
        ]

        # Add packages based on content
        for chapter in chapters:
            if chapter.tables:
                if "booktabs" not in packages:
                    packages.append("booktabs")
            if chapter.illustrations_prompts:
                if "float" not in packages:
                    packages.append("float")

        # Subject-specific packages
        if "machine learning" in profile.subject_area.lower():
            packages.extend(["algorithm", "algorithmic"])

        if "math" in profile.subject_area.lower():
            packages.append("proof")

        return packages

    async def _chapter_to_latex(
        self,
        chapter: Chapter,
        profile: BookProfile,
    ) -> str:
        """Convert chapter to LaTeX.

        Args:
            chapter: Chapter object
            profile: Book profile

        Returns:
            LaTeX code
        """
        lines = []

        # Chapter header
        lines.append(f"\\chapter{{{chapter.title}}}")
        lines.append("")

        # Introduction
        if chapter.introduction:
            lines.append(chapter.introduction)
            lines.append("")

        # Theory section
        if chapter.theory:
            lines.append("\\section{Theory}")
            lines.append(chapter.theory)
            lines.append("")

        # Definitions section
        if chapter.definitions:
            lines.append("\\section{Definitions}")
            lines.append(chapter.definitions)
            lines.append("")

        # Examples section
        if chapter.examples:
            lines.append("\\section{Examples}")
            for i, example in enumerate(chapter.examples, 1):
                lines.append(f"\\subsection{{Example {i}}}")
                lines.append(example)
                lines.append("")

        # Exercises section
        if chapter.exercises:
            lines.append("\\section{Exercises}")
            for i, exercise in enumerate(chapter.exercises, 1):
                lines.append(f"\\subsection{{Exercise {i}}}")
                lines.append(exercise)
                lines.append("")

        # MCQs section
        if chapter.mcqs:
            lines.append("\\section{Multiple Choice Questions}")
            for mcq in chapter.mcqs:
                lines.append(await self._mcq_to_latex(mcq))
                lines.append("")

        # Summary section
        if chapter.summary:
            lines.append("\\section{Summary}")
            lines.append(chapter.summary)
            lines.append("")

        # References section
        if chapter.references:
            lines.append("\\section{References}")
            lines.append("\\begin{thebibliography}{99}")
            for ref in chapter.references:
                lines.append(f"\\bibitem{{{ref[:20].replace(' ', '_')}}} {ref}")
            lines.append("\\end{thebibliography}")
            lines.append("")

        return "\n".join(lines)

    async def _mcq_to_latex(self, mcq: dict) -> str:
        """Convert MCQ to LaTeX format.

        Args:
            mcq: MCQ dict

        Returns:
            LaTeX code
        """
        lines = [
            f"\\textbf{{Q: {mcq.get('question', '')}}} \\\\",
        ]

        for i, option in enumerate(mcq.get("options", [])):
            lines.append(option + " \\\\ ")

        correct = mcq.get("correct", "")
        explanation = mcq.get("explanation", "")
        lines.append(f"\\textit{{Answer: {correct}. {explanation}}}")

        return "\n".join(lines)
