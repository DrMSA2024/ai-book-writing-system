"""Book type selector agent."""

from typing import Dict, List
from loguru import logger

from src.agents.base_agent import BaseAgent
from src.models.book_profile import BookType
from src.api.deepseek_client import DeepSeekClient
from src.memory.memory_manager import MemoryManager


class BookTypeAgent(BaseAgent):
    """Determines book specialization and type."""

    def __init__(
        self,
        api_client: DeepSeekClient,
        memory_manager: MemoryManager,
    ):
        """Initialize book type agent.

        Args:
            api_client: DeepSeek API client
            memory_manager: Memory manager
        """
        super().__init__(
            name="BookTypeAgent",
            description="Determines book type and specialization",
            api_client=api_client,
            memory_manager=memory_manager,
        )
        self.book_types = [
            BookType.ACADEMIC_TEXTBOOK,
            BookType.RESEARCH_MONOGRAPH,
            BookType.TECHNICAL_HANDBOOK,
            BookType.COMPETITIVE_EXAM,
            BookType.LAB_MANUAL,
            BookType.NOVEL,
            BookType.BIOGRAPHY,
            BookType.SELF_HELP,
            BookType.CHILDRENS_BOOK,
            BookType.QUESTION_BANK,
        ]

    async def execute(
        self,
        title: str,
        subject_area: str,
        book_type: str = "",
    ) -> Dict[str, str]:
        """Determine book type and specialization.

        Args:
            title: Book title
            subject_area: Subject area
            book_type: Suggested book type (empty for auto-detection)

        Returns:
            Dict with type and specialization
        """
        self.log_info(f"Analyzing book type for: {title}")

        if book_type:
            self.log_info(f"Using specified book type: {book_type}")
            return {
                "type": book_type,
                "confidence": "100%",
                "reason": "User specified",
            }

        # Auto-detect using AI
        try:
            prompt = f"""
Analyze this book title and subject area to determine the best book type.

Title: {title}
Subject Area: {subject_area}

Available types:
{", ".join(str(bt) for bt in self.book_types)}

Respond with JSON format:
{{
    "type": "<selected type>",
    "confidence": "<percentage>",
    "reason": "<brief explanation>",
    "specialization": "<specific focus area>"
}}
"""
            result = await self.api_client.generate_json(
                prompt,
                system_prompt="You are a book classification expert. Analyze the given book title and subject to determine its most appropriate type.",
                temperature=0.3,
                max_tokens=300,
            )

            if result and "type" in result:
                self.log_info(f"Auto-detected type: {result['type']}")
                return result
            else:
                self.log_error("Failed to parse detection result")
                return {
                    "type": "Academic Textbook",
                    "confidence": "50%",
                    "reason": "Detection failed, using default",
                }

        except Exception as e:
            self.log_error(f"Type detection failed: {e}")
            return {
                "type": "Academic Textbook",
                "confidence": "50%",
                "reason": "Detection failed, using default",
            }

    async def get_template_suggestions(self, book_type: str) -> List[str]:
        """Get LaTeX template suggestions for book type.

        Args:
            book_type: Type of book

        Returns:
            List of suggested templates
        """
        suggestions = {
            "Academic Textbook": ["book", "report"],
            "Research Monograph": ["book", "springer", "elsevier"],
            "Technical Handbook": ["book", "taylor_francis"],
            "Competitive Exam Book": ["book", "report"],
            "Lab Manual": ["report", "article"],
            "Novel": ["book"],
            "Biography": ["book"],
            "Self Help": ["book"],
            "Children's Book": ["book"],
            "Question Bank": ["article", "report"],
        }
        return suggestions.get(book_type, ["book"])
