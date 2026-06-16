"""Book profile data models."""

from enum import Enum
from typing import Optional, List
from pydantic import BaseModel, Field
from datetime import datetime


class BookType(str, Enum):
    """Supported book types."""
    ACADEMIC_TEXTBOOK = "Academic Textbook"
    RESEARCH_MONOGRAPH = "Research Monograph"
    TECHNICAL_HANDBOOK = "Technical Handbook"
    COMPETITIVE_EXAM = "Competitive Exam Book"
    LAB_MANUAL = "Lab Manual"
    NOVEL = "Novel"
    BIOGRAPHY = "Biography"
    SELF_HELP = "Self Help"
    CHILDRENS_BOOK = "Children's Book"
    QUESTION_BANK = "Question Bank"
    USER_DEFINED = "User Defined"


class WritingStyle(str, Enum):
    """Supported writing styles."""
    FORMAL = "Formal"
    CONVERSATIONAL = "Conversational"
    STORY_BASED = "Story Based"
    SIMPLE = "Simple"
    MINIMALISTIC = "Minimalistic"
    ACADEMIC = "Academic"
    USER_DEFINED = "User Defined"


class AcademicLevel(str, Enum):
    """Academic levels."""
    SCHOOL = "School"
    UNDERGRADUATE = "Undergraduate"
    POSTGRADUATE = "Postgraduate"
    PROFESSIONAL = "Professional"
    GENERAL = "General"


class BookProfile(BaseModel):
    """Complete book profile."""
    
    # Basic Information
    title: str = Field(..., description="Book title")
    author: str = Field(..., description="Author name")
    subject_area: str = Field(..., description="Subject area/domain")
    
    # Book Classification
    book_type: BookType = Field(
        default=BookType.ACADEMIC_TEXTBOOK,
        description="Type of book"
    )
    writing_style: WritingStyle = Field(
        default=WritingStyle.FORMAL,
        description="Writing style"
    )
    academic_level: AcademicLevel = Field(
        default=AcademicLevel.UNDERGRADUATE,
        description="Academic level"
    )
    
    # Content Configuration
    target_readers: str = Field(
        ..., description="Target audience description"
    )
    language: str = Field(default="English", description="Book language")
    
    # Page/Content Targets
    total_pages: int = Field(
        default=300, description="Target total pages"
    )
    chapters_count: Optional[int] = Field(
        default=None, description="Number of chapters (auto if None)"
    )
    
    # Features
    include_examples: bool = Field(
        default=True, description="Include examples"
    )
    include_exercises: bool = Field(
        default=True, description="Include exercises"
    )
    include_illustrations: bool = Field(
        default=True, description="Include illustrations"
    )
    include_bibliography: bool = Field(
        default=True, description="Include bibliography"
    )
    include_index: bool = Field(
        default=True, description="Include index"
    )
    include_glossary: bool = Field(
        default=False, description="Include glossary"
    )
    
    # LaTeX Configuration
    latex_template: str = Field(
        default="book", description="LaTeX template (book, report, springer, etc.)"
    )
    
    # Quality Settings
    humanization_level: str = Field(
        default="natural",
        description="Humanization level (natural, strict, slight_imperfections)"
    )
    ai_score_target: float = Field(
        default=0.10, description="Target AI score (below this value)"
    )
    
    # Metadata
    created_at: datetime = Field(
        default_factory=datetime.now, description="Creation timestamp"
    )
    updated_at: datetime = Field(
        default_factory=datetime.now, description="Last update timestamp"
    )
    notes: Optional[str] = Field(
        default=None, description="Additional notes"
    )
    
    class Config:
        """Pydantic config."""
        use_enum_values = False

    def __str__(self) -> str:
        """String representation."""
        return f"BookProfile(title='{self.title}', author='{self.author}', type={self.book_type})"

    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return self.dict()

    @classmethod
    def from_dict(cls, data: dict) -> "BookProfile":
        """Create from dictionary."""
        return cls(**data)
