"""Chapter data models."""

from typing import List, Optional
from pydantic import BaseModel, Field
from datetime import datetime


class ChapterSection(BaseModel):
    """Section within a chapter."""
    
    title: str = Field(..., description="Section title")
    content: str = Field(..., description="Section content")
    subsections: List["ChapterSection"] = Field(
        default_factory=list, description="Subsections"
    )
    
    class Config:
        """Pydantic config."""
        arbitrary_types_allowed = True


class Chapter(BaseModel):
    """Book chapter."""
    
    # Identification
    chapter_number: int = Field(..., description="Chapter number")
    title: str = Field(..., description="Chapter title")
    
    # Content
    introduction: Optional[str] = Field(
        default=None, description="Chapter introduction"
    )
    body: Optional[str] = Field(
        default=None, description="Main chapter body"
    )
    sections: List[ChapterSection] = Field(
        default_factory=list, description="Chapter sections"
    )
    
    # Optional Components
    definitions: Optional[str] = Field(
        default=None, description="Key definitions"
    )
    theory: Optional[str] = Field(
        default=None, description="Theoretical content"
    )
    examples: List[str] = Field(
        default_factory=list, description="Examples"
    )
    counterexamples: List[str] = Field(
        default_factory=list, description="Counterexamples"
    )
    illustrations_prompts: List[str] = Field(
        default_factory=list, description="Image prompts"
    )
    tables: List[dict] = Field(
        default_factory=list, description="Tables"
    )
    exercises: List[str] = Field(
        default_factory=list, description="Exercises"
    )
    mcqs: List[dict] = Field(
        default_factory=list, description="Multiple choice questions"
    )
    summary: Optional[str] = Field(
        default=None, description="Chapter summary"
    )
    references: List[str] = Field(
        default_factory=list, description="References"
    )
    
    # Metadata
    estimated_pages: int = Field(
        default=20, description="Estimated page count"
    )
    actual_pages: Optional[int] = Field(
        default=None, description="Actual page count"
    )
    word_count: Optional[int] = Field(
        default=None, description="Word count"
    )
    writing_style: Optional[str] = Field(
        default=None, description="Writing style used"
    )
    created_at: datetime = Field(
        default_factory=datetime.now, description="Creation time"
    )
    updated_at: datetime = Field(
        default_factory=datetime.now, description="Last update time"
    )
    is_humanized: bool = Field(
        default=False, description="Whether humanized"
    )
    ai_score: Optional[float] = Field(
        default=None, description="AI-generated content score"
    )
    
    class Config:
        """Pydantic config."""
        arbitrary_types_allowed = True
    
    def get_full_content(self) -> str:
        """Get complete chapter content.
        
        Returns:
            Full chapter content
        """
        content_parts = []
        
        if self.introduction:
            content_parts.append(self.introduction)
        
        if self.theory:
            content_parts.append(f"## Theory\n\n{self.theory}")
        
        if self.definitions:
            content_parts.append(f"## Definitions\n\n{self.definitions}")
        
        if self.examples:
            content_parts.append(f"## Examples\n\n" + "\n\n".join(self.examples))
        
        if self.counterexamples:
            content_parts.append(
                f"## Counterexamples\n\n" + "\n\n".join(self.counterexamples)
            )
        
        if self.exercises:
            content_parts.append(
                f"## Exercises\n\n" + "\n\n".join(self.exercises)
            )
        
        if self.summary:
            content_parts.append(f"## Summary\n\n{self.summary}")
        
        return "\n\n".join(content_parts)
    
    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return self.dict()
