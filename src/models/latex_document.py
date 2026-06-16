"""LaTeX document models."""

from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from enum import Enum


class LaTeXTemplate(str, Enum):
    """Supported LaTeX templates."""
    BOOK = "book"
    REPORT = "report"
    ARTICLE = "article"
    SPRINGER = "springer"
    ELSEVIER = "elsevier"
    TAYLOR_FRANCIS = "taylor_francis"
    IEEE = "ieee"


class LaTeXDocument(BaseModel):
    """LaTeX document representation."""
    
    title: str = Field(..., description="Document title")
    author: str = Field(..., description="Document author")
    template: LaTeXTemplate = Field(
        default=LaTeXTemplate.BOOK,
        description="LaTeX template to use"
    )
    
    # Preamble
    packages: List[str] = Field(
        default_factory=list, description="LaTeX packages"
    )
    custom_preamble: Optional[str] = Field(
        default=None, description="Custom preamble code"
    )
    
    # Content
    main_content: str = Field(
        default="", description="Main document content"
    )
    chapters: List[str] = Field(
        default_factory=list, description="Chapter contents"
    )
    
    # References
    bibliography_file: Optional[str] = Field(
        default=None, description="Bibliography file path"
    )
    bibliography_style: str = Field(
        default="plain", description="Bibliography style"
    )
    
    # Optional Components
    has_index: bool = Field(default=False, description="Include index")
    has_glossary: bool = Field(default=False, description="Include glossary")
    has_appendices: bool = Field(default=False, description="Include appendices")
    
    # Metadata
    date: Optional[str] = Field(default=None, description="Document date")
    subject: Optional[str] = Field(default=None, description="PDF subject")
    keywords: List[str] = Field(
        default_factory=list, description="PDF keywords"
    )
    
    class Config:
        """Pydantic config."""
        use_enum_values = False
    
    def add_chapter(self, content: str) -> None:
        """Add chapter content.
        
        Args:
            content: Chapter LaTeX code
        """
        self.chapters.append(content)
    
    def get_preamble(self) -> str:
        """Generate LaTeX preamble.
        
        Returns:
            LaTeX preamble code
        """
        lines = []
        
        # Document class
        if self.template == LaTeXTemplate.SPRINGER:
            lines.append(r"\documentclass{svbook}")
        elif self.template == LaTeXTemplate.ELSEVIER:
            lines.append(r"\documentclass{elsarticle}")
        elif self.template == LaTeXTemplate.IEEE:
            lines.append(r"\documentclass{IEEEtran}")
        else:
            doc_class = self.template.value if isinstance(self.template, LaTeXTemplate) else self.template
            lines.append(f"\\documentclass{{{doc_class}}}")
        
        lines.append("")
        
        # Packages
        default_packages = [
            "amsmath",
            "amssymb",
            "graphicx",
            "hyperref",
            "xcolor",
        ]
        
        for pkg in default_packages:
            if pkg not in self.packages:
                self.packages.append(pkg)
        
        for pkg in self.packages:
            lines.append(f"\\usepackage{{{pkg}}}")
        
        lines.append("")
        
        # Document info
        lines.append(f"\\title{{{self.title}}}")
        lines.append(f"\\author{{{self.author}}}")
        
        if self.date:
            lines.append(f"\\date{{{self.date}}}")
        else:
            lines.append(r"\date{\today}")
        
        lines.append("")
        
        # Custom preamble
        if self.custom_preamble:
            lines.append(self.custom_preamble)
            lines.append("")
        
        return "\n".join(lines)
    
    def get_document_body(self) -> str:
        """Generate document body.
        
        Returns:
            LaTeX document body
        """
        lines = [r"\begin{document}"]
        lines.append(r"\maketitle")
        lines.append(r"\tableofcontents")
        lines.append("")
        
        # Add chapters
        for chapter in self.chapters:
            lines.append(chapter)
        
        # Bibliography
        if self.bibliography_file:
            lines.append("")
            lines.append(f"\\bibliographystyle{{{self.bibliography_style}}}")
            lines.append(f"\\bibliography{{{self.bibliography_file}}}")
        
        # Index
        if self.has_index:
            lines.append("")
            lines.append(r"\printindex")
        
        # Glossary
        if self.has_glossary:
            lines.append("")
            lines.append(r"\printglossaries")
        
        lines.append("")
        lines.append(r"\end{document}")
        
        return "\n".join(lines)
    
    def to_latex(self) -> str:
        """Generate complete LaTeX document.
        
        Returns:
            Complete LaTeX code
        """
        preamble = self.get_preamble()
        body = self.get_document_body()
        return f"{preamble}\n\n{body}"
    
    def to_file(self, filepath: str) -> None:
        """Write to LaTeX file.
        
        Args:
            filepath: Output file path
        """
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(self.to_latex())
