"""Image prompt generation agent."""

from typing import List, Dict
from loguru import logger
import json

from src.agents.base_agent import BaseAgent
from src.api.deepseek_client import DeepSeekClient
from src.memory.memory_manager import MemoryManager


class ImagePromptAgent(BaseAgent):
    """Generates prompts for AI image generation."""

    def __init__(
        self,
        api_client: DeepSeekClient,
        memory_manager: MemoryManager,
    ):
        """Initialize image prompt agent.

        Args:
            api_client: DeepSeek API client
            memory_manager: Memory manager
        """
        super().__init__(
            name="ImagePromptAgent",
            description="Generates prompts for image generation systems",
            api_client=api_client,
            memory_manager=memory_manager,
        )
        self.platforms = [
            "DALL-E",
            "Midjourney",
            "Flux",
            "Stable Diffusion",
        ]
        self.styles = [
            "Technical diagram",
            "Line diagram",
            "Flowchart",
            "Infographic",
            "Concept diagram",
            "Educational illustration",
            "3D visualization",
            "Realistic",
        ]

    async def execute(
        self,
        topic: str,
        chapter_title: str,
        illustration_type: str = "Technical diagram",
        platforms: List[str] = None,
    ) -> List[Dict[str, str]]:
        """Generate image prompts.

        Args:
            topic: Topic for illustrations
            chapter_title: Chapter title for context
            illustration_type: Type of illustration
            platforms: Target platforms (defaults to all)

        Returns:
            List of prompt dicts
        """
        self.log_info(f"Generating prompts for: {topic}")

        if platforms is None:
            platforms = self.platforms

        try:
            prompts = []

            for platform in platforms:
                prompt = await self._generate_platform_prompt(
                    topic, chapter_title, illustration_type, platform
                )
                prompts.append(prompt)

            if self.memory_manager:
                await self.memory_manager.store_image_prompts(
                    chapter_title, prompts
                )

            self.log_info(f"Generated {len(prompts)} prompts")
            return prompts

        except Exception as e:
            self.log_error(f"Prompt generation failed: {e}")
            raise

    async def _generate_platform_prompt(
        self,
        topic: str,
        chapter_title: str,
        illustration_type: str,
        platform: str,
    ) -> Dict[str, str]:
        """Generate platform-specific prompt.

        Args:
            topic: Topic
            chapter_title: Chapter title
            illustration_type: Illustration type
            platform: Target platform

        Returns:
            Prompt dict
        """
        platform_instructions = {
            "DALL-E": "Use natural language description, focus on composition and style",
            "Midjourney": "Use concise, descriptive language with emphasis on aesthetic; include --ar aspect ratio",
            "Flux": "Use detailed, technical descriptions with specific visual elements",
            "Stable Diffusion": "Use comma-separated tags and descriptors",
        }

        instructions = platform_instructions.get(
            platform, "Create a detailed visual description"
        )

        prompt_request = f"""
Create a detailed image prompt for {platform} to generate a {illustration_type} for:

Topic: {topic}
Chapter: {chapter_title}
Platform: {platform}

Instructions: {instructions}

Respond with JSON:
{{
    "platform": "{platform}",
    "main_prompt": "<main description>",
    "style": "<visual style>",
    "composition": "<composition details>",
    "negative_prompt": "<what to avoid>",
    "aspect_ratio": "<ratio like 16:9>",
    "rendering_instructions": "<specific instructions>"
}}
"""

        result = await self.api_client.generate_json(
            prompt_request,
            system_prompt="You are an expert in creating prompts for AI image generation. Provide detailed, effective prompts optimized for each platform.",
            temperature=0.7,
            max_tokens=500,
        )

        return result if result else {"platform": platform, "main_prompt": topic}

    async def generate_cover_prompt(
        self,
        book_title: str,
        subject_area: str,
        style: str = "Professional",
        platforms: List[str] = None,
    ) -> List[Dict[str, str]]:
        """Generate cover page prompts.

        Args:
            book_title: Book title
            subject_area: Subject area
            style: Cover style
            platforms: Target platforms

        Returns:
            List of cover prompts
        """
        self.log_info(f"Generating cover prompts for: {book_title}")

        if platforms is None:
            platforms = self.platforms

        cover_topic = (
            f"{style} book cover for '{book_title}' about {subject_area}"
        )

        return await self.execute(
            topic=cover_topic,
            chapter_title="Cover",
            illustration_type="Book cover",
            platforms=platforms,
        )
