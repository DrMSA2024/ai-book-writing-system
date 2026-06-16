"""Main workflow orchestration."""

import asyncio
from typing import Optional, List
from loguru import logger
from pathlib import Path

from src.api.deepseek_client import DeepSeekClient
from src.memory.memory_manager import MemoryManager
from src.models.book_profile import BookProfile
from src.models.chapter import Chapter
from src.models.latex_document import LaTeXDocument
from src.agents.book_profile_agent import BookProfileAgent
from src.agents.book_type_agent import BookTypeAgent
from src.agents.toc_agent import TOCAgent
from src.agents.chapter_writer_agent import ChapterWriterAgent
from src.agents.expansion_agent import ExpansionAgent
from src.agents.image_prompt_agent import ImagePromptAgent
from src.agents.latex_agent import LaTeXAgent
from src.agents.latex_error_agent import LaTeXErrorAgent
from src.agents.humanization_agent import HumanizationAgent
from src.agents.qa_agent import QAAgent
from src.config import Config
from src.orchestration.state_manager import StateManager, WorkflowState
from src.utils.file_manager import FileManager


class BookWritingWorkflow:
    """Orchestrates the complete book writing workflow."""

    def __init__(self):
        """Initialize workflow."""
        self.api_client = DeepSeekClient()
        self.memory_manager = MemoryManager(
            db_path=Config.MEMORY_DB,
            vector_store_path=Config.CHROMADB_PATH,
        )
        self.state_manager = StateManager()
        self.file_manager = FileManager(Config.BOOKS_DIR)

        # Initialize agents
        self.book_profile_agent = BookProfileAgent(
            self.api_client, self.memory_manager
        )
        self.book_type_agent = BookTypeAgent(
            self.api_client, self.memory_manager
        )
        self.toc_agent = TOCAgent(self.api_client, self.memory_manager)
        self.chapter_writer_agent = ChapterWriterAgent(
            self.api_client, self.memory_manager
        )
        self.expansion_agent = ExpansionAgent(
            self.api_client, self.memory_manager
        )
        self.image_prompt_agent = ImagePromptAgent(
            self.api_client, self.memory_manager
        )
        self.latex_agent = LaTeXAgent(
            self.api_client, self.memory_manager
        )
        self.latex_error_agent = LaTeXErrorAgent(
            self.api_client, self.memory_manager
        )
        self.humanization_agent = HumanizationAgent(
            self.api_client, self.memory_manager
        )
        self.qa_agent = QAAgent(self.api_client, self.memory_manager)

        logger.info("Workflow initialized with all agents")

    async def execute(
        self,
        profile: BookProfile,
        skip_stages: Optional[List[str]] = None,
    ) -> dict:
        """Execute complete book writing workflow.

        Args:
            profile: Book profile
            skip_stages: Stages to skip (for development/testing)

        Returns:
            Workflow result dict
        """
        skip_stages = skip_stages or []

        try:
            logger.info(f"Starting workflow for: {profile.title}")
            self.state_manager.set_state(
                WorkflowState.PROFILE_CREATED,
                {"profile": profile.dict()},
            )

            # Create book directory
            book_dir = self.file_manager.create_book_directory(
                profile.title
            )

            # Stage 1: Determine book type
            if "book_type" not in skip_stages:
                logger.info("Stage 1: Determining book type")
                type_result = await self.book_type_agent.execute(
                    profile.title,
                    profile.subject_area,
                    profile.book_type,
                )
                self.state_manager.set_state(
                    WorkflowState.TYPE_DETERMINED,
                    {"type_result": type_result},
                )
                logger.info(f"Book type: {type_result['type']}")

            # Stage 2: Generate TOC
            if "toc" not in skip_stages:
                logger.info("Stage 2: Generating table of contents")
                async with DeepSeekClient() as api:
                    toc = await self.toc_agent.execute(profile)
                self.state_manager.set_state(
                    WorkflowState.TOC_GENERATED,
                    {"toc_total_chapters": toc.total_chapters},
                )
                logger.info(
                    f"TOC generated with {toc.total_chapters} chapters"
                )

            # Stage 3: Write chapters
            if "chapters" not in skip_stages:
                logger.info("Stage 3: Writing chapters")
                self.state_manager.set_state(
                    WorkflowState.CHAPTERS_WRITING
                )

                chapters: List[Chapter] = []
                for i in range(toc.total_chapters):
                    logger.info(f"Writing chapter {i+1}/{toc.total_chapters}")
                    chapter = await self.chapter_writer_agent.execute(
                        chapter_number=i + 1,
                        title=f"Chapter {i+1}",
                        profile=profile,
                        previous_chapter_summary=(
                            chapters[-1].summary if chapters else None
                        ),
                    )
                    chapters.append(chapter)

                self.state_manager.set_state(
                    WorkflowState.CHAPTERS_WRITTEN,
                    {"chapters_count": len(chapters)},
                )

            # Stage 4: Expand chapters
            if "expansion" not in skip_stages:
                logger.info("Stage 4: Expanding chapters")
                pages_per_chapter = profile.total_pages // len(chapters)

                for chapter in chapters:
                    await self.expansion_agent.execute(
                        chapter, profile, pages_per_chapter
                    )

                self.state_manager.set_state(
                    WorkflowState.EXPANSION_DONE
                )

            # Stage 5: Generate image prompts
            if "images" not in skip_stages:
                logger.info("Stage 5: Generating image prompts")
                for chapter in chapters:
                    if chapter.illustrations_prompts:
                        await self.image_prompt_agent.execute(
                            topic=chapter.title,
                            chapter_title=chapter.title,
                        )

                self.state_manager.set_state(
                    WorkflowState.IMAGES_GENERATED
                )

            # Stage 6: Generate LaTeX
            if "latex" not in skip_stages:
                logger.info("Stage 6: Generating LaTeX")
                latex_doc = await self.latex_agent.execute(
                    profile, chapters, template=profile.latex_template
                )
                self.state_manager.set_state(
                    WorkflowState.LATEX_GENERATED
                )

                # Save LaTeX
                latex_file = self.file_manager.save_latex(
                    book_dir, latex_doc.to_latex()
                )

            # Stage 7: Humanize text
            if "humanization" not in skip_stages:
                logger.info("Stage 7: Humanizing text")
                for chapter in chapters:
                    result = await self.humanization_agent.execute(
                        chapter.get_full_content(),
                        level=profile.humanization_level,
                        target_ai_score=profile.ai_score_target,
                    )
                    chapter.is_humanized = result["target_met"]
                    chapter.ai_score = result["estimated_ai_score"]

                self.state_manager.set_state(
                    WorkflowState.HUMANIZED
                )

            # Stage 8: QA checks
            if "qa" not in skip_stages:
                logger.info("Stage 8: Running QA checks")
                qa_report = await self.qa_agent.execute(
                    chapters, profile
                )
                self.state_manager.set_state(
                    WorkflowState.QA_PASSED,
                    {"qa_status": qa_report["overall_status"]},
                )
                logger.info(f"QA Result: {qa_report['overall_status']}")

            self.state_manager.set_state(WorkflowState.COMPLETED)

            return {
                "status": "success",
                "book_title": profile.title,
                "book_dir": str(book_dir),
                "chapters": len(chapters),
                "state": self.state_manager.get_state().value,
            }

        except Exception as e:
            logger.error(f"Workflow failed: {e}")
            self.state_manager.set_state(
                WorkflowState.FAILED,
                {"error": str(e)},
            )
            return {
                "status": "failed",
                "error": str(e),
                "state": self.state_manager.get_state().value,
            }
