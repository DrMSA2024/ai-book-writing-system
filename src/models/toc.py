"""Table of Contents data models."""

from typing import List, Optional
from pydantic import BaseModel, Field


class TOCItem(BaseModel):
    """Single TOC item (chapter, section, subsection)."""
    
    level: int = Field(..., description="Nesting level (1=chapter, 2=section, 3=subsection)")
    number: str = Field(..., description="Item number (1, 1.1, 1.1.1)")
    title: str = Field(..., description="Item title")
    page: Optional[int] = Field(default=None, description="Page number")
    estimated_pages: Optional[int] = Field(default=None, description="Estimated page count")
    children: List["TOCItem"] = Field(default_factory=list, description="Child items")
    
    class Config:
        """Pydantic config."""
        arbitrary_types_allowed = True


class TableOfContents(BaseModel):
    """Complete table of contents."""
    
    book_title: str = Field(..., description="Book title")
    total_chapters: int = Field(..., description="Total number of chapters")
    items: List[TOCItem] = Field(default_factory=list, description="TOC items")
    
    def add_chapter(self, number: int, title: str, estimated_pages: int = 20) -> TOCItem:
        """Add a chapter to TOC.
        
        Args:
            number: Chapter number
            title: Chapter title
            estimated_pages: Estimated pages for chapter
            
        Returns:
            Created TOCItem
        """
        item = TOCItem(
            level=1,
            number=str(number),
            title=title,
            estimated_pages=estimated_pages,
        )
        self.items.append(item)
        return item
    
    def add_section(
        self,
        chapter_number: int,
        section_number: int,
        title: str,
        estimated_pages: int = 5,
    ) -> Optional[TOCItem]:
        """Add section to a chapter.
        
        Args:
            chapter_number: Chapter number
            section_number: Section number within chapter
            title: Section title
            estimated_pages: Estimated pages
            
        Returns:
            Created TOCItem or None if chapter not found
        """
        chapter = None
        for item in self.items:
            if item.number == str(chapter_number):
                chapter = item
                break
        
        if not chapter:
            return None
        
        section = TOCItem(
            level=2,
            number=f"{chapter_number}.{section_number}",
            title=title,
            estimated_pages=estimated_pages,
        )
        chapter.children.append(section)
        return section
    
    def get_total_estimated_pages(self) -> int:
        """Calculate total estimated pages.
        
        Returns:
            Total estimated pages
        """
        total = 0
        for item in self.items:
            if item.estimated_pages:
                total += item.estimated_pages
            for child in item.children:
                if child.estimated_pages:
                    total += child.estimated_pages
        return total
    
    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return self.dict()
