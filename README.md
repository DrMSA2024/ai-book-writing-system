# Production-Ready Autonomous Multi-Agent Book Writing System

## Overview

A sophisticated Python-based autonomous book writing system using DeepSeek API, featuring multiple specialized AI agents working collaboratively to generate complete, publication-ready books in LaTeX and PDF formats.

## Features

### Core Capabilities
- ✅ Multi-agent architecture with 10 specialized AI agents
- ✅ Automatic book type detection and specialization
- ✅ Hierarchical book structure generation (Parts → Chapters → Sections)
- ✅ Dynamic content expansion based on page targets
- ✅ AI-generated images prompts (DALL-E, Midjourney, Flux, Stable Diffusion)
- ✅ Complete LaTeX generation with multiple templates
- ✅ Automatic LaTeX error detection and correction
- ✅ Text humanization to reduce AI fingerprints (AI Score < 10%)
- ✅ Quality assurance and consistency verification
- ✅ PDF compilation and export

### Supported Book Types
1. Academic Textbook
2. Research Monograph
3. Technical Handbook
4. Competitive Exam Book
5. Lab Manual
6. Novel
7. Biography
8. Self Help
9. Children's Book
10. Question Bank
11. User Defined

### AI Agents
1. **Book Profile Agent** - Gathers book requirements
2. **Book Type Selector** - Determines specialization
3. **TOC Agent** - Generates table of contents
4. **Chapter Writer Agent** - Writes book chapters
5. **Chapter Expansion Agent** - Expands content to page targets
6. **Image Prompt Agent** - Generates image prompts
7. **LaTeX Agent** - Generates LaTeX code
8. **LaTeX Error Correction Agent** - Fixes compilation errors
9. **Humanization Agent** - Reduces AI fingerprints
10. **Quality Assurance Agent** - Verifies completeness

## Project Structure

```
ai-book-writing-system/
├── src/
│   ├── __init__.py
│   ├── config.py                 # Configuration management
│   ├── api/
│   │   ├── __init__.py
│   │   ├── deepseek_client.py    # DeepSeek API wrapper
│   │   └── rate_limiter.py       # Rate limiting
│   ├── models/
│   │   ├── __init__.py
│   │   ├── book_profile.py       # Book profile schema
│   │   ├── toc.py                # Table of contents schema
│   │   ├── chapter.py            # Chapter schema
│   │   └── latex_document.py     # LaTeX document schema
│   ├── agents/
│   │   ├── __init__.py
│   │   ├── base_agent.py         # Base agent class
│   │   ├── book_profile_agent.py # Book profile agent
│   │   ├── book_type_agent.py    # Book type selector
│   │   ├── toc_agent.py          # TOC generation
│   │   ├── chapter_writer_agent.py # Chapter writing
│   │   ├── expansion_agent.py    # Content expansion
│   │   ├── image_prompt_agent.py # Image prompt generation
│   │   ├── latex_agent.py        # LaTeX generation
│   │   ├── latex_error_agent.py  # Error correction
│   │   ├── humanization_agent.py # Text humanization
│   │   └── qa_agent.py           # Quality assurance
│   ├── memory/
│   │   ├── __init__.py
│   │   ├── database.py           # SQLite wrapper
│   │   ├── vector_store.py       # ChromaDB wrapper
│   │   └── memory_manager.py     # Memory orchestration
│   ├── latex/
│   │   ├── __init__.py
│   │   ├── compiler.py           # LaTeX compilation
│   │   ├── templates.py          # LaTeX templates
│   │   └── error_handler.py      # Error handling
│   ├── utils/
│   │   ├── __init__.py
│   │   ├── logger.py             # Logging setup
│   │   ├── validators.py         # Input validation
│   │   ├── text_processor.py     # Text utilities
│   │   └── file_manager.py       # File operations
│   └── orchestration/
│       ├── __init__.py
│       ├── workflow.py           # Main workflow
│       └── state_manager.py      # State management
├── ui/
│   ├── __init__.py
│   ├── cli.py                    # Command-line interface
│   └── streamlit_app.py          # Streamlit GUI
├── tests/
│   ├── __init__.py
│   ├── test_api.py
│   ├── test_agents.py
│   ├── test_memory.py
│   ├── test_latex.py
│   └── test_integration.py
├── examples/
│   ├── generate_sample_book.py   # Sample execution
│   └── sample_config.yaml        # Example configuration
├── data/
│   ├── books/                    # Generated books
│   ├── memory.db                 # SQLite database
│   └── chromadb/                 # Vector store
├── .env.example
├── .gitignore
├── requirements.txt
├── setup.py
└── README.md
```

## Installation

### Prerequisites
- Python 3.12+
- LaTeX/pdflatex (for PDF compilation)
- DeepSeek API Key

### Setup

1. Clone the repository:
```bash
git clone https://github.com/DrMSA2024/ai-book-writing-system.git
cd ai-book-writing-system
```

2. Create virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Install LaTeX (if not already installed):

**Ubuntu/Debian:**
```bash
sudo apt-get install texlive-full latexmk
```

**macOS:**
```bash
brew install basictex latexmk
```

**Windows:**
Download and install MiKTeX from https://miktex.org/

5. Configure environment:
```bash
cp .env.example .env
# Edit .env and add your DeepSeek API key
```

## Quick Start

### CLI Usage

```bash
python -m ui.cli
```

Follows interactive prompts to:
1. Enter book title and author information
2. Select book type
3. Configure writing parameters
4. Generate table of contents
5. Write chapters
6. Expand content
7. Generate images
8. Compile PDF

### Streamlit GUI

```bash
streamlit run ui/streamlit_app.py
```

Access at `http://localhost:8501`

### Programmatic Usage

```python
from src.orchestration.workflow import BookWritingWorkflow
from src.models.book_profile import BookProfile

# Create workflow
workflow = BookWritingWorkflow()

# Define book profile
profile = BookProfile(
    title="Machine Learning Fundamentals",
    author="Dr. AI",
    subject_area="Computer Science",
    book_type="Academic Textbook",
    academic_level="Undergraduate",
    target_readers="Computer Science Students",
    writing_style="Formal",
    total_pages=300
)

# Execute workflow
result = await workflow.execute(profile)

# Export outputs
result.export_pdf("output.pdf")
result.export_latex("output.tex")
```

## Configuration

### Environment Variables (.env)

```
DEEPSEEK_API_KEY=your_key_here
DEEPSEEK_MODEL=deepseek-chat
BOOK_OUTPUT_DIR=./books
LOG_LEVEL=INFO
```

### Book Configuration

Supported book types:
- Academic Textbook
- Research Monograph
- Technical Handbook
- Competitive Exam Book
- Lab Manual
- Novel
- Biography
- Self Help
- Children's Book
- Question Bank

Writing styles:
- Formal
- Conversational
- Story Based
- Simple
- Minimalistic
- Academic
- User Defined

## API Integration

### DeepSeek API

The system uses DeepSeek API for:
- Content generation
- Structure planning
- Error analysis
- Text humanization
- Quality checks

**Rate Limiting:** 10 requests/minute (configurable)
**Timeout:** 60 seconds
**Retry Logic:** Exponential backoff with 3 attempts

## Memory System

### SQLite Database

Stores:
- Book metadata
- Chapter information
- Writing progress
- Configuration settings

### ChromaDB Vector Store

Indexes:
- Chapter content for semantic search
- Writing style embeddings
- Reference documents
- Generated examples

## LaTeX Support

### Document Classes
- book
- report
- article

### Templates
- Standard (book class)
- Springer
- Elsevier
- Taylor and Francis
- IEEE

### Features
- Automatic package management
- TikZ diagram support
- Bibliography generation
- Index and glossary
- Cross-references
- Equation numbering
- Figure/table captions

## Text Humanization

Reduces AI fingerprints through:
- Natural sentence variation
- Human-like transitions
- Varied paragraph structure
- Conversational tone (optional)
- Slight imperfections (optional)

**AI Score Target:** < 10%

## Quality Assurance

Verifies:
- Content consistency
- Fact accuracy
- Reference integrity
- Cross-reference validity
- Chapter/section numbering
- Image/table/exercise numbering
- Page count targets
- Bibliography completeness

## Example: Generating a Sample Book

```bash
python examples/generate_sample_book.py
```

Generates "Machine Learning Fundamentals" academic textbook with:
- Complete TOC
- 5 comprehensive chapters
- Mathematical equations
- Code examples
- End-of-chapter exercises
- Bibliography
- PDF export

## Testing

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src

# Run specific test file
pytest tests/test_agents.py
```

## Performance

- Chapter generation: ~30-60 seconds per chapter
- Content expansion: ~20-30 seconds per expansion level
- LaTeX compilation: ~10-15 seconds per document
- Total book generation: ~5-10 minutes (300 pages)

## Troubleshooting

### LaTeX Compilation Errors

1. Ensure LaTeX is installed: `pdflatex --version`
2. Check for missing packages in error logs
3. System will auto-correct common errors
4. Manual review in `/temp/latex_errors.log`

### API Rate Limiting

1. Check API key validity
2. Verify rate limit configuration in .env
3. Review logs: `tail -f logs/app.log`

### Memory Issues

1. Clear ChromaDB cache: `rm -rf data/chromadb`
2. Reset SQLite: `rm data/memory.db`
3. Check disk space: `df -h`

## Contributing

Contributions welcome! Please:
1. Fork the repository
2. Create feature branch
3. Add tests for new functionality
4. Submit pull request

## License

MIT License - See LICENSE file

## Support

For issues and questions:
1. Check documentation
2. Review example files
3. Check existing issues
4. Create new issue with details

## Roadmap

- [ ] Multi-language support
- [ ] Advanced PDF styling
- [ ] Real-time collaboration
- [ ] Version control for drafts
- [ ] Advanced image generation integration
- [ ] Export to Word, ePub, Markdown
- [ ] AI model switching
- [ ] Custom prompt templates
