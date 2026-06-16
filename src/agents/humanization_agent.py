"""Text humanization agent."""

from typing import Dict, Optional
from loguru import logger

from src.agents.base_agent import BaseAgent
from src.api.deepseek_client import DeepSeekClient
from src.memory.memory_manager import MemoryManager


class HumanizationAgent(BaseAgent):
    """Humanizes AI-generated text to reduce AI fingerprints."""

    def __init__(
        self,
        api_client: DeepSeekClient,
        memory_manager: MemoryManager,
    ):
        """Initialize humanization agent.

        Args:
            api_client: DeepSeek API client
            memory_manager: Memory manager
        """
        super().__init__(
            name="HumanizationAgent",
            description="Humanizes text to reduce AI fingerprints",
            api_client=api_client,
            memory_manager=memory_manager,
        )
        self.humanization_levels = {
            "natural": "Natural writing with human transitions",
            "strict": "Strict grammar and perfect punctuation",
            "slight_imperfections": "Natural with occasional minor imperfections",
        }

    async def execute(
        self,
        text: str,
        level: str = "natural",
        target_ai_score: float = 0.10,
    ) -> Dict[str, any]:
        """Humanize text.

        Args:
            text: Text to humanize
            level: Humanization level
            target_ai_score: Target AI score

        Returns:
            Dict with humanized text and metrics
        """
        self.log_info(f"Humanizing text (level={level})")

        try:
            humanized = await self._humanize_text(text, level)
            ai_score = await self._estimate_ai_score(humanized)

            result = {
                "original_text": text,
                "humanized_text": humanized,
                "estimated_ai_score": ai_score,
                "target_met": ai_score < target_ai_score,
                "level": level,
            }

            self.log_info(
                f"Humanization complete. AI Score: {ai_score:.2%}"
            )
            return result

        except Exception as e:
            self.log_error(f"Humanization failed: {e}")
            return {
                "original_text": text,
                "humanized_text": text,
                "estimated_ai_score": 0.5,
                "target_met": False,
                "level": level,
                "error": str(e),
            }

    async def _humanize_text(self, text: str, level: str) -> str:
        """Apply humanization to text.

        Args:
            text: Text to humanize
            level: Humanization level

        Returns:
            Humanized text
        """
        level_desc = self.humanization_levels.get(
            level, self.humanization_levels["natural"]
        )

        prompt = f"""
Rewrite this text to make it sound more human and less like AI-generated content.

Humanization Level: {level_desc}

Guide:
- Vary sentence length naturally
- Use more contractions and casual language
- Add natural transitions and connectors
- Avoid repetitive sentence structures
- Reduce overly formal tone
- Make it more conversational

Original Text:
{text}

Provide the humanized version:
"""

        humanized = await self.api_client.generate_text(
            prompt,
            system_prompt="You are an expert at making AI text sound human. Preserve all information while improving naturalness.",
            temperature=0.7,
            max_tokens=len(text.split()) + 100,
        )

        return humanized or text

    async def _estimate_ai_score(self, text: str) -> float:
        """Estimate probability text is AI-generated.

        Args:
            text: Text to analyze

        Returns:
            Estimated AI score (0-1)
        """
        # Simple heuristics for demonstration
        score = 0.0

        # Check for common AI patterns
        ai_indicators = [
            "can be summarized",
            "in conclusion",
            "it is important to note",
            "furthermore",
            "moreover",
            "therefore",
            "to summarize",
            "ultimately",
        ]

        text_lower = text.lower()
        for indicator in ai_indicators:
            if indicator in text_lower:
                score += 0.05

        # Check sentence length uniformity (AI tends to be uniform)
        sentences = text.split(".")
        if len(sentences) > 3:
            lengths = [len(s.split()) for s in sentences if s.strip()]
            if lengths:
                avg_length = sum(lengths) / len(lengths)
                variance = sum((l - avg_length) ** 2 for l in lengths) / len(
                    lengths
                )
                if variance < 10:  # Low variance = more AI-like
                    score += 0.1

        # Check for passive voice (AI tendency)
        if "is" in text_lower and "was" in text_lower:
            score += 0.05

        # Normalize score
        score = min(score, 0.7)  # Cap at 70%
        return max(score, 0.0)

    async def analyze_text_for_ai_fingerprints(
        self, text: str
    ) -> Dict[str, any]:
        """Analyze text for AI fingerprints.

        Args:
            text: Text to analyze

        Returns:
            Analysis dict
        """
        analysis = {
            "text_length": len(text),
            "word_count": len(text.split()),
            "sentence_count": len(text.split(".")),
            "ai_indicators_found": [],
            "estimated_ai_score": 0.0,
        }

        # Check for indicators
        indicators = {
            "formal_transitions": ["furthermore", "moreover", "therefore"],
            "passive_voice_patterns": ["is mentioned", "is stated"],
            "repetitive_openings": ["this", "it", "the"],
            "formal_language": ["utilize", "implement", "facilitate"],
        }

        text_lower = text.lower()
        for category, terms in indicators.items():
            found = [t for t in terms if t in text_lower]
            if found:
                analysis["ai_indicators_found"].append(
                    {"category": category, "terms": found}
                )

        analysis["estimated_ai_score"] = await self._estimate_ai_score(
            text
        )

        return analysis
