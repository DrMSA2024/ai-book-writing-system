"""Setup configuration for package."""

from setuptools import setup, find_packages
from pathlib import Path

this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text(encoding="utf-8")

setup(
    name="ai-book-writing-system",
    version="1.0.0",
    description="Production-ready Autonomous Multi-Agent Book Writing System using DeepSeek API",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="AI Architecture Team",
    author_email="ai@example.com",
    url="https://github.com/DrMSA2024/ai-book-writing-system",
    license="MIT",
    packages=find_packages(),
    python_requires=">=3.12",
    install_requires=[
        "python-dotenv==1.0.1",
        "requests==2.31.0",
        "aiohttp==3.9.5",
        "pydantic==2.7.4",
        "rich==13.7.0",
        "loguru==0.7.2",
        "numpy==1.24.3",
        "pandas==2.2.1",
        "networkx==3.3",
        "pylatex==1.4.2",
        "bibtexparser==2.0.0",
        "tenacity==8.2.3",
        "sentence-transformers==2.7.0",
        "chromadb==0.4.24",
        "tiktoken==0.7.0",
        "streamlit==1.35.0",
    ],
    extras_require={
        "dev": [
            "pytest==7.4.4",
            "pytest-asyncio==0.23.3",
            "pytest-cov==4.1.0",
            "black==24.3.0",
            "flake8==7.0.0",
            "mypy==1.10.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "book-cli=src.ui.cli:main",
        ],
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Text Processing",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.12",
    ],
    keywords="ai book writing deepseek agent autonomous",
)
