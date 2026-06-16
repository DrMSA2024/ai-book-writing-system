# Autonomous Multi-Agent Book Writing System

## Quick Start

### Installation

```bash
# Clone repository
git clone https://github.com/DrMSA2024/ai-book-writing-system.git
cd ai-book-writing-system

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Install LaTeX
sudo apt-get install texlive-full latexmk  # Ubuntu/Debian
brew install basictex latexmk              # macOS
# Windows: Download MiKTeX from https://miktex.org/

# Setup configuration
cp .env.example .env
# Edit .env and add your DeepSeek API key
```

### CLI Usage

```bash
python -m src.ui.cli
```

Follows interactive prompts to create a new book.

### Streamlit GUI

```bash
streamlit run ui/streamlit_app.py
```

Access at `http://localhost:8501`

### Example Script

```bash
python examples/generate_sample_book.py
```

Generates "Machine Learning Fundamentals" book.

## System Architecture

```
AI Book Writing System
├── Book Profile Agent (Gathers requirements)
├── Book Type Agent (Determines specialization)
├── TOC Agent (Generates structure)
├── Chapter Writer Agent (Writes content)
├── Expansion Agent (Meets page targets)
├── Image Prompt Agent (Generates image prompts)
├── LaTeX Agent (Generates LaTeX code)
├── LaTeX Error Agent (Fixes compilation errors)
├── Humanization Agent (Reduces AI fingerprints)
└── QA Agent (Quality assurance)

Support Systems:
├── DeepSeek API Client (with rate limiting & retry)
├── SQLite Database (book metadata & chapters)
├── ChromaDB Vector Store (semantic search)
├── File Manager (book organization)
└── State Manager (workflow tracking)
```

## Configuration

### Environment Variables (.env)

```
# DeepSeek API
DEEPSEEK_API_KEY=your_api_key_here
DEEPSEEK_MODEL=deepseek-chat

# Paths
BOOK_OUTPUT_DIR=./books
TEMP_DIR=./temp

# Memory
MEMORY_DB=./data/memory.db
CHROMADB_PATH=./data/chromadb

# Logging
LOG_LEVEL=INFO
```

## Usage Examples

### Programmatic API

```python
from src.models.book_profile import BookProfile, BookType
from src.orchestration.workflow import BookWritingWorkflow
import asyncio

async def create_book():
    profile = BookProfile(
        title="My Book",
        author="My Name",
        subject_area="Python Programming",
        book_type=BookType.TECHNICAL_HANDBOOK,
        total_pages=250
    )
    
    workflow = BookWritingWorkflow()
    result = await workflow.execute(profile)
    return result

asyncio.run(create_book())
```

### Creating Custom Agents

```python
from src.agents.base_agent import BaseAgent
from src.api.deepseek_client import DeepSeekClient

class CustomAgent(BaseAgent):
    def __init__(self, api_client, memory_manager):
        super().__init__(
            name="CustomAgent",
            description="Custom implementation",
            api_client=api_client,
            memory_manager=memory_manager
        )
    
    async def execute(self, *args, **kwargs):
        # Your implementation here
        pass
```

## Features in Detail

### Book Types Supported
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

### Writing Styles
- Formal
- Conversational
- Story Based
- Simple
- Minimalistic
- Academic

### LaTeX Templates
- Standard (book/report)
- Springer
- Elsevier
- Taylor & Francis
- IEEE

### AI Humanization
- Natural sentence variation
- Human-like transitions
- Varied paragraph structure
- Customizable imperfection levels
- AI score tracking (target < 10%)

### Quality Assurance
- Content consistency checks
- Fact accuracy verification
- Cross-reference validation
- Numbering consistency
- Page count verification

## API Integration

### DeepSeek API Features
- Automatic retry with exponential backoff
- Token usage tracking
- Rate limiting (10 req/min default)
- Configurable timeout
- Streaming support

### Memory System

**SQLite Database:**
- Book metadata storage
- Chapter content persistence
- Settings management
- Historical data

**ChromaDB Vector Store:**
- Semantic chapter search
- Style embeddings
- Cross-chapter consistency
- Content deduplication

## Performance

- Chapter generation: 30-60 seconds
- Content expansion: 20-30 seconds per level
- LaTeX compilation: 10-15 seconds
- Total book (300 pages): 5-10 minutes

## Testing

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src

# Run specific test
pytest tests/test_system.py::TestBookProfile
```

## Troubleshooting

### LaTeX Errors
1. Ensure LaTeX is installed: `pdflatex --version`
2. Check error logs in `/temp/latex_errors.log`
3. System auto-corrects common errors

### API Issues
1. Verify DeepSeek API key in .env
2. Check rate limit: 10 requests/minute
3. Review logs: `tail -f logs/app.log`

### Memory Issues
1. Clear ChromaDB: `rm -rf data/chromadb`
2. Reset database: `rm data/memory.db`
3. Check disk space: `df -h`

## Development

### Code Style
```bash
black src/
flake8 src/
mypy src/
```

### Adding New Agents
1. Inherit from `BaseAgent`
2. Implement `execute()` method
3. Add to workflow orchestration
4. Write unit tests

## Contributing

1. Fork repository
2. Create feature branch
3. Add tests for new functionality
4. Submit pull request

## License

MIT License - See LICENSE file

## Roadmap

- [ ] Multi-language support
- [ ] Advanced PDF styling
- [ ] Real-time collaboration
- [ ] Version control for drafts
- [ ] Image generation integration
- [ ] Export to Word, ePub, Markdown
- [ ] Custom prompt templates
- [ ] Model switching capability

## Support

For issues and questions:
1. Check documentation
2. Review example files
3. Check existing issues
4. Create new issue with details

## Citation

If you use this system in your research, please cite:

```bibtex
@software{book_writing_system_2024,
  title = {Autonomous Multi-Agent Book Writing System},
  author = {AI Architecture Team},
  year = {2024},
  url = {https://github.com/DrMSA2024/ai-book-writing-system}
}
```

---

**Made with ❤️ by AI Architects | Powered by DeepSeek API**
