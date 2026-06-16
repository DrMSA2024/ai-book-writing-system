"""Command-line interface for book writing system."""

import asyncio
from typing import Optional
from pathlib import Path
from rich.console import Console
from rich.table import Table
from rich.prompt import Prompt, Confirm
from rich.panel import Panel
from loguru import logger

from src.models.book_profile import BookProfile, BookType, WritingStyle, AcademicLevel
from src.orchestration.workflow import BookWritingWorkflow
from src.config import Config


class CLIInterface:
    """Command-line interface."""

    def __init__(self):
        """Initialize CLI."""
        self.console = Console()
        self.workflow: Optional[BookWritingWorkflow] = None

    def print_banner(self) -> None:
        """Print application banner."""
        banner = """
    ╔═══════════════════════════════════════════════════════════╗
    ║   Autonomous Multi-Agent Book Writing System v1.0.0      ║
    ║   Powered by DeepSeek API & Python                       ║
    ╚═══════════════════════════════════════════════════════════╝
        """
        self.console.print(banner, style="cyan bold")

    def print_menu(self) -> None:
        """Print main menu."""
        menu_text = """
    1. Create New Book
    2. Resume Book
    3. Edit TOC
    4. View Books
    5. Settings
    6. Exit
        """
        self.console.print(Panel(menu_text, title="Main Menu", border_style="blue"))

    def gather_book_profile(self) -> BookProfile:
        """Gather book profile from user input.

        Returns:
            BookProfile object
        """
        self.console.print("\n[bold cyan]📚 Book Profile Setup[/bold cyan]\n")

        # Title
        title = Prompt.ask("📖 Book Title")

        # Author
        author = Prompt.ask("✍️  Author Name")

        # Subject Area
        subject = Prompt.ask("📚 Subject Area")

        # Book Type
        self.console.print("\n[bold]Book Type:[/bold]")
        for i, book_type in enumerate(BookType, 1):
            self.console.print(f"  {i}. {book_type.value}")
        
        type_choice = Prompt.ask("Select book type", choices=[str(i) for i in range(1, len(BookType) + 1)])
        book_type = list(BookType)[int(type_choice) - 1]

        # Academic Level
        self.console.print("\n[bold]Academic Level:[/bold]")
        for i, level in enumerate(AcademicLevel, 1):
            self.console.print(f"  {i}. {level.value}")
        
        level_choice = Prompt.ask("Select academic level", choices=[str(i) for i in range(1, len(AcademicLevel) + 1)])
        academic_level = list(AcademicLevel)[int(level_choice) - 1]

        # Writing Style
        self.console.print("\n[bold]Writing Style:[/bold]")
        for i, style in enumerate(WritingStyle, 1):
            self.console.print(f"  {i}. {style.value}")
        
        style_choice = Prompt.ask("Select writing style", choices=[str(i) for i in range(1, len(WritingStyle) + 1)])
        writing_style = list(WritingStyle)[int(style_choice) - 1]

        # Target Readers
        target_readers = Prompt.ask("Target Readers (e.g., 'Computer Science Students')")

        # Pages
        total_pages = int(Prompt.ask("Total Pages Target", default="300"))

        # Create profile
        profile = BookProfile(
            title=title,
            author=author,
            subject_area=subject,
            book_type=book_type,
            academic_level=academic_level,
            writing_style=writing_style,
            target_readers=target_readers,
            language="English",
            total_pages=total_pages,
        )

        self.console.print("\n[green]✓ Profile created successfully![/green]\n")
        return profile

    async def create_new_book(self) -> None:
        """Create a new book."""
        try:
            # Gather profile
            profile = self.gather_book_profile()

            # Show confirmation
            self.console.print("\n[bold cyan]Book Profile Summary:[/bold cyan]")
            summary_table = Table(show_header=False, box=None)
            summary_table.add_row("Title:", profile.title)
            summary_table.add_row("Author:", profile.author)
            summary_table.add_row("Type:", profile.book_type)
            summary_table.add_row("Pages:", str(profile.total_pages))
            self.console.print(summary_table)

            if not Confirm.ask("\nProceed with book creation?"):
                self.console.print("[yellow]Cancelled.[/yellow]")
                return

            # Initialize workflow
            self.workflow = BookWritingWorkflow()

            # Execute workflow
            self.console.print("\n[bold cyan]🚀 Starting book writing workflow...[/bold cyan]\n")
            result = await self.workflow.execute(profile)

            if result["status"] == "success":
                self.console.print(
                    f"\n[green bold]✓ Book created successfully![/green bold]\n"
                )
                self.console.print(f"  Location: {result['book_dir']}")
                self.console.print(f"  Chapters: {result['chapters']}")
            else:
                self.console.print(
                    f"\n[red]✗ Book creation failed: {result.get('error')}[/red]\n"
                )

        except Exception as e:
            logger.error(f"Error creating book: {e}")
            self.console.print(f"[red]Error: {e}[/red]")

    def view_books(self) -> None:
        """Display list of created books."""
        self.console.print("\n[bold cyan]📚 Your Books[/bold cyan]\n")

        # Get books from memory
        from src.memory.memory_manager import MemoryManager
        memory = MemoryManager(
            db_path=Config.MEMORY_DB,
            vector_store_path=Config.CHROMADB_PATH,
        )

        books = memory.get_all_books()

        if not books:
            self.console.print("[yellow]No books found.[/yellow]")
            return

        table = Table(title="Books", show_header=True, header_style="bold")
        table.add_column("Title", style="cyan")
        table.add_column("Author", style="magenta")
        table.add_column("Type", style="green")
        table.add_column("Pages", style="yellow")

        for book in books:
            table.add_row(
                book["title"],
                book["author"],
                book["book_type"],
                str(book["total_pages"]),
            )

        self.console.print(table)

    def run(self) -> None:
        """Run CLI application."""
        self.print_banner()

        while True:
            self.print_menu()
            choice = Prompt.ask("Select option", choices=["1", "2", "3", "4", "5", "6"])

            if choice == "1":
                asyncio.run(self.create_new_book())
            elif choice == "2":
                self.console.print("[yellow]Resume feature coming soon...[/yellow]")
            elif choice == "3":
                self.console.print("[yellow]TOC editing feature coming soon...[/yellow]")
            elif choice == "4":
                self.view_books()
            elif choice == "5":
                self.console.print("[yellow]Settings feature coming soon...[/yellow]")
            elif choice == "6":
                self.console.print("[cyan]Thank you for using Book Writing System![/cyan]")
                break


def main() -> None:
    """Main entry point."""
    Config.setup()
    Config.validate()
    cli = CLIInterface()
    cli.run()


if __name__ == "__main__":
    main()
