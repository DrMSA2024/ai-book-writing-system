"""Quality Assurance agent."""

from typing import Dict, List, Optional
from loguru import logger

from src.agents.base_agent import BaseAgent
from src.models.chapter import Chapter
from src.models.book_profile import BookProfile
from src.api.deepseek_client import DeepSeekClient
from src.memory.memory_manager import MemoryManager


class QAAgent(BaseAgent):
    """Quality assurance and verification agent."""

    def __init__(
        self,
        api_client: DeepSeekClient,
        memory_manager: MemoryManager,
    ):
        """Initialize QA agent.

        Args:
            api_client: DeepSeek API client
            memory_manager: Memory manager
        """
        super().__init__(
            name="QAAgent",
            description="Performs quality assurance checks on generated content",
            api_client=api_client,
            memory_manager=memory_manager,
        )

    async def execute(
        self,
        chapters: List[Chapter],
        profile: BookProfile,
    ) -> Dict[str, any]:
        """Perform comprehensive QA checks.

        Args:
            chapters: List of chapters
            profile: Book profile

        Returns:
            QA report dict
        """
        self.log_info("Starting QA checks")

        try:
            report = {
                "profile_validation": await self._validate_profile(profile),
                "chapter_checks": await self._check_chapters(chapters),
                "consistency_checks": await self._check_consistency(chapters),
                "content_checks": await self._check_content_quality(chapters),
                "numbering_checks": await self._check_numbering(chapters),
                "issues_found": [],
                "warnings": [],
                "overall_status": "PASS",
            }

            # Compile issues and warnings
            for check_result in report.values():
                if isinstance(check_result, dict):
                    if not check_result.get("passed", True):
                        report["issues_found"].append(
                            check_result.get("message", "Unknown issue")
                        )
                    if check_result.get("warnings"):
                        report["warnings"].extend(
                            check_result["warnings"]
                        )

            if report["issues_found"]:
                report["overall_status"] = "FAIL"
            elif report["warnings"]:
                report["overall_status"] = "PASS WITH WARNINGS"

            self.log_info(f"QA check complete: {report['overall_status']}")
            return report

        except Exception as e:
            self.log_error(f"QA check failed: {e}")
            return {
                "overall_status": "ERROR",
                "error": str(e),
            }

    async def _validate_profile(self, profile: BookProfile) -> Dict:
        """Validate book profile.

        Args:
            profile: Book profile

        Returns:
            Validation result
        """
        issues = []

        if not profile.title or len(profile.title) < 3:
            issues.append("Invalid book title")

        if not profile.author or len(profile.author) < 3:
            issues.append("Invalid author name")

        if profile.total_pages < 50:
            issues.append("Book too short (minimum 50 pages)")

        return {
            "passed": len(issues) == 0,
            "message": "; ".join(issues) if issues else "Profile valid",
        }

    async def _check_chapters(self, chapters: List[Chapter]) -> Dict:
        """Check chapter integrity.

        Args:
            chapters: List of chapters

        Returns:
            Check result
        """
        issues = []
        warnings = []

        for i, chapter in enumerate(chapters):
            if not chapter.title:
                issues.append(f"Chapter {i+1} missing title")

            if not chapter.introduction and not chapter.body:
                issues.append(f"Chapter {i+1} has no content")

            if (
                chapter.chapter_number != i + 1
            ):  # Check numbering
                warnings.append(
                    f"Chapter numbering mismatch at position {i+1}"
                )

        return {
            "passed": len(issues) == 0,
            "message": f"Checked {len(chapters)} chapters",
            "issues": issues,
            "warnings": warnings,
        }

    async def _check_consistency(
        self, chapters: List[Chapter]
    ) -> Dict:
        """Check content consistency across chapters.

        Args:
            chapters: List of chapters

        Returns:
            Check result
        """
        warnings = []

        # Check for consistent writing styles
        if chapters:
            first_style = chapters[0].writing_style
            for i, chapter in enumerate(chapters[1:], 1):
                if (
                    chapter.writing_style
                    and chapter.writing_style != first_style
                ):
                    warnings.append(
                        f"Chapter {i+1} has different writing style"
                    )

        return {
            "passed": len(warnings) == 0,
            "message": "Consistency check complete",
            "warnings": warnings,
        }

    async def _check_content_quality(
        self, chapters: List[Chapter]
    ) -> Dict:
        """Check content quality metrics.

        Args:
            chapters: List of chapters

        Returns:
            Check result
        """
        issues = []
        warnings = []

        for i, chapter in enumerate(chapters):
            content = chapter.get_full_content()
            word_count = len(content.split())

            if word_count < 500:
                warnings.append(
                    f"Chapter {i+1} may be too short ({word_count} words)"
                )

            # Check for common issues
            if "TODO" in content or "FIXME" in content:
                issues.append(
                    f"Chapter {i+1} contains unfinished markers"
                )

        return {
            "passed": len(issues) == 0,
            "message": "Quality check complete",
            "issues": issues,
            "warnings": warnings,
        }

    async def _check_numbering(
        self, chapters: List[Chapter]
    ) -> Dict:
        """Check numbering consistency.

        Args:
            chapters: List of chapters

        Returns:
            Check result
        """
        issues = []

        # Check chapter numbers are sequential
        for i, chapter in enumerate(chapters):
            if chapter.chapter_number != i + 1:
                issues.append(
                    f"Chapter numbering error at position {i+1}"
                )

        return {
            "passed": len(issues) == 0,
            "message": "Numbering check complete",
            "issues": issues,
        }
